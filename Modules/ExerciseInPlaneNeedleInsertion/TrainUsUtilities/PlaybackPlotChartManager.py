from __main__ import vtk, slicer
import logging
from itertools import groupby

#------------------------------------------------------------------------------
#
# PlaybackPlotChartManager
#
#------------------------------------------------------------------------------
class PlaybackPlotChartManager:
  """
  Enable the creation of plot charts to visualize metric values during sequence playback.

  How to use:

  (1) Register computed metric values using the "addNewMetric" function

    Example:
      >> myPlaybackPlotChartManager.addNewMetric('DistanceFromNeedleTipToUsPlane', distanceValues)
      >> myPlaybackPlotChartManager.addNewMetric('AngleBetweenNeedleTipAndUsPlane', angleValues)

  (2) Register the timestamps for those metrics

    Example:
      >> myPlaybackPlotChartManager.addMetricTimestamps(timestampValues)

  (3) Create the plot chart

    Example:
      >> myPlaybackPlotChartManager.createPlotChart()

  (4) Select the metric you want to visualize using the "updatePlotChart" function

    Example:
      >> myPlaybackPlotChartManager.updatePlotChart('AngleBetweenNeedleTipAndUsPlane')

  (*) If you want to show a cursor to indicate the corresponding metric value during playback,
      you can do the following:

      - Create plot with "cursor" parameter equal to True: 
          >> myPlaybackPlotChartManager.createPlotChart(cursor = True)

      - Update cursor position for each new sample in the recording:
          >> myPlaybackPlotChartManager.updateCursorPosition(currentTimestamp)
  """

  #------------------------------------------------------------------------------
  def __init__( self ):
    # Dictionary to store metric values
    self.metricData_dict = {}

    # List to store timestamp values
    self.metricTimestamps_list = {}

    # List to store metric names
    self.metricNames_list = []

    # Table nodes
    self.metricTableNode = None
    self.cursorTableNode = None  

    # Plot series nodes
    self.metricPlotSeries_dict = {}
    self.cursorPlotSeries_dict = {}

    # Plot chart node
    self.plotChartNode = None

    # Cursor
    self.cursorEnabled = False

  #------------------------------------------------------------------------------
  def getPlotChart(self):
    return self.plotChartNode

  #------------------------------------------------------------------------------
  def addNewMetric(self, metricName, metricValues):
    """
    Register new metric to be displayed in plot chart.    
    :param metricName: metric name (string)
    :param metricValues: list of metric values (list)
    """
    # Add new metric to dictionary
    self.metricData_dict[metricName] = list(metricValues)

    # Update list of metric names
    self.metricNames_list = self.getListOfMetrics()

  #------------------------------------------------------------------------------
  def addMetricTimestamps(self, timestampValues):
    """
    Register timestamps corresponding to metric values.    
    :param timestampValues: list of timestamps (list)
    """
    # Update list of metric timestamps
    self.metricTimestamps_list.clear() # delete content
    self.metricTimestamps_list = list(timestampValues)

  #------------------------------------------------------------------------------
  def getListOfMetrics(self):
    return list(self.metricData_dict.keys())

  #------------------------------------------------------------------------------
  def getNumberOfSamplesInMetric(self, metricName):
    metricValues = self.metricData_dict[metricName]
    numSamples = len(metricValues)
    return numSamples

  #------------------------------------------------------------------------------
  def getNumberOfSamples(self):
    # Get number of samples in all metrics in dictionary
    numSamples_list = []
    for metricName in self.metricNames_list:
      numSamples_list.append(self.getNumberOfSamplesInMetric(metricName))

    # Check if all metrics have the same number of samples
    success = self.allValuesEqual(numSamples_list)

    # Output
    if success:
      numSamples = numSamples_list[0] # any value in list, all are equal
    else:
      logging.error('Metrics stored in dictionary do not have the same number of samples.')
      numSamples = None
    return numSamples

  #------------------------------------------------------------------------------
  def createMetricTable(self):
    # Get number of metrics
    numMetrics = len(self.metricNames_list)

    # Get number of samples in recording
    numSamples = self.getNumberOfSamples()

    # Delete existing table node if any
    if self.metricTableNode:
      slicer.mrmlScene.RemoveNode(self.metricTableNode)
      self.metricTableNode = None    

    # Create table node
    self.metricTableNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLTableNode')
    self.metricTableNode.SetName('Metrics')
    self.metricTableNode.SetLocked(True) # lock table to avoid modifications
    self.metricTableNode.RemoveAllColumns() # reset

    # Get table from node
    table = self.metricTableNode.GetTable()    

    # Add one column for timestamp and one column for each metric
    array = vtk.vtkFloatArray()
    array.SetName('timestamp')
    table.AddColumn(array)
    for metricName in self.metricNames_list:
      array = vtk.vtkFloatArray()
      array.SetName(metricName)
      table.AddColumn(array)

    # Fill table
    table.SetNumberOfRows(numSamples)
    ## Add timestamps
    timestampValues = self.metricTimestamps_list
    for sampleID in range(numSamples):
      table.SetValue(sampleID, 0, timestampValues[sampleID])
    ## Add metric values
    for metricID in range(numMetrics):
      metricValues = self.metricData_dict[self.metricNames_list[metricID]]
      for sampleID in range(numSamples):
        table.SetValue(sampleID, metricID+1, metricValues[sampleID])
    table.Modified()

  #------------------------------------------------------------------------------
  def createCursorTable(self):
    # Get number of metrics
    numMetrics = len(self.metricNames_list)

    # Delete existing table node if any
    if self.cursorTableNode:
      slicer.mrmlScene.RemoveNode(self.cursorTableNode)
      self.cursorTableNode = None

    # Create table node
    self.cursorTableNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLTableNode')
    self.cursorTableNode.SetName('Cursor')
    self.cursorTableNode.SetLocked(True) # lock table to avoid modifications
    self.cursorTableNode.RemoveAllColumns() # reset

    # Get table from node
    table = self.cursorTableNode.GetTable()

    # Add one column for timestamp and one column for each metric
    array = vtk.vtkFloatArray()
    array.SetName('timestamp')
    table.AddColumn(array)
    for metricName in self.metricNames_list:
      array = vtk.vtkFloatArray()
      array.SetName(metricName)
      table.AddColumn(array)

    # Fill table
    table.SetNumberOfRows(1)
    ## Add minimum timestamp value
    timestampValues = self.metricTimestamps_list
    table.SetValue(0, 0, min(timestampValues[:]))
    ## Add metric values
    for metricID in range(numMetrics):
      metricValues = self.metricData_dict[self.metricNames_list[metricID]]
      table.SetValue(0, metricID+1, max(metricValues[:]))
    table.Modified()

  #------------------------------------------------------------------------------
  def createMetricPlotSeries(self):
    # Define plot series settings
    plotMarkerSize = 15
    plotLineWidth = 4
    plotColor = [1,0,0] # red

    # Delete previous plot series
    if self.metricPlotSeries_dict:
      for key in self.metricPlotSeries_dict.keys():
        slicer.mrmlScene.RemoveNode(self.metricPlotSeries_dict[key])
      self.metricPlotSeries_dict = {}

    # Create plot series
    self.metricPlotSeries_dict = {}
    for metricName in self.metricNames_list:
      plotSeriesNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLPlotSeriesNode')
      plotSeriesNode.SetName(metricName)
      plotSeriesNode.SetAndObserveTableNodeID(self.metricTableNode.GetID())
      plotSeriesNode.SetXColumnName('timestamp')
      plotSeriesNode.SetYColumnName(metricName)
      plotSeriesNode.SetPlotType(slicer.vtkMRMLPlotSeriesNode.PlotTypeScatter)
      plotSeriesNode.SetMarkerStyle(slicer.vtkMRMLPlotSeriesNode.MarkerStyleNone)
      plotSeriesNode.SetMarkerSize(plotMarkerSize)
      plotSeriesNode.SetLineWidth(plotLineWidth)
      plotSeriesNode.SetColor(plotColor)
      self.metricPlotSeries_dict[metricName] = plotSeriesNode

  #------------------------------------------------------------------------------
  def createCursorPlotSeries(self):
    # Define plot series settings
    plotMarkerSize = 15
    plotLineWidth = 4
    plotColor = [0,0,0] # black

    # Delete previous cursor plot series
    if self.cursorPlotSeries_dict:
      for key in self.cursorPlotSeries_dict.keys():
        slicer.mrmlScene.RemoveNode(self.cursorPlotSeries_dict[key])
      self.cursorPlotSeries_dict = {}

    # Create cursor plot series
    self.cursorPlotSeries_dict = {}
    for metricName in self.metricNames_list:
      plotSeriesNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLPlotSeriesNode')
      plotSeriesNode.SetName(metricName + '_Cursor')
      plotSeriesNode.SetAndObserveTableNodeID(self.cursorTableNode.GetID())
      plotSeriesNode.SetXColumnName('timestamp')
      plotSeriesNode.SetYColumnName(metricName)
      plotSeriesNode.SetPlotType(slicer.vtkMRMLPlotSeriesNode.PlotTypeScatterBar)
      plotSeriesNode.SetMarkerStyle(slicer.vtkMRMLPlotSeriesNode.MarkerStyleCircle)
      plotSeriesNode.SetMarkerSize(plotMarkerSize)
      plotSeriesNode.SetLineWidth(plotLineWidth)
      plotSeriesNode.SetColor(plotColor)
      self.cursorPlotSeries_dict[metricName] = plotSeriesNode

  #------------------------------------------------------------------------------
  def createPlotChart(self, cursor = False):
    """
    Create plot chart to display registered metrics relative to corresponding timestamps.
    """
    # Ensure metric data is available
    if not self.metricData_dict:
      logging.error('No metric data. Plot chart will not be created.')
      return

    # Ensure timestamp data is available
    if not self.metricTimestamps_list:
      logging.error('No timestamp data. Plot chart will not be created.')
      return

    # Enable cursor
    self.cursorEnabled = cursor

    # Create metric table
    self.createMetricTable()

    # Create cursor table
    if self.cursorEnabled:
      self.createCursorTable()

    # Create plot series
    self.createMetricPlotSeries()

    # Create cursor plot series
    if self.cursorEnabled:
      self.createCursorPlotSeries()

    # Delete previous plot chart
    if self.plotChartNode:
      slicer.mrmlScene.RemoveNode(self.plotChartNode)
      self.plotChartNode = None

    # Create plot chart
    self.plotChartNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLPlotChartNode')
    self.plotChartNode.SetName('Chart')
    self.plotChartNode.RemoveAllPlotSeriesNodeIDs() # reset
    self.plotChartNode.SetTitle('Metric Plot')
    self.plotChartNode.SetXAxisTitle('Timestamp')
    #self.plotChartNode.SetYAxisTitle('ANGLE (\xB0)')
    self.plotChartNode.SetAxisLabelFontSize(20)
    self.plotChartNode.LegendVisibilityOff() # hide legend
    self.plotChartNode.GridVisibilityOff()

    # Select first metric
    listOfMetrics = self.getListOfMetrics()
    firstMetricName = listOfMetrics[0]
    self.plotChartNode.AddAndObservePlotSeriesNodeID(self.metricPlotSeries_dict[firstMetricName].GetID())
    if self.cursorEnabled:
      self.plotChartNode.AddAndObservePlotSeriesNodeID(self.cursorPlotSeries_dict[firstMetricName].GetID())

  #------------------------------------------------------------------------------
  def updatePlotChart(self, selectedMetricName):
    """
    Update visible plot series in plot chart.
    """
    listOfMetrics = self.getListOfMetrics()
    if (selectedMetricName in listOfMetrics) and (self.plotChartNode):
      self.plotChartNode.RemoveAllPlotSeriesNodeIDs() # reset
      self.plotChartNode.AddAndObservePlotSeriesNodeID(self.metricPlotSeries_dict[selectedMetricName].GetID())
      if self.cursorEnabled:
        self.plotChartNode.AddAndObservePlotSeriesNodeID(self.cursorPlotSeries_dict[selectedMetricName].GetID())
      self.plotChartNode.SetTitle(selectedMetricName)

  #------------------------------------------------------------------------------
  def updateCursorPosition(self, itemID):
    """
    Modify timestamp value in cursor table to force plot chart update.
    """
    if self.cursorTableNode:
      table = self.cursorTableNode.GetTable()
      table.SetValue(0, 0, float(itemID))
      table.Modified()

  #------------------------------------------------------------------------------
  def removeAssociatedNodesFromScene(self):
    """
    Removes associated nodes from Slicer scene.
    """
    # Delete table nodes
    if self.metricTableNode:
      slicer.mrmlScene.RemoveNode(self.metricTableNode)
      self.metricTableNode = None
    if self.cursorTableNode:
      slicer.mrmlScene.RemoveNode(self.cursorTableNode)
      self.cursorTableNode = None

    # Delete plot series nodes
    if self.metricPlotSeries_dict:
      for key in self.metricPlotSeries_dict.keys():
        slicer.mrmlScene.RemoveNode(self.metricPlotSeries_dict[key])
      self.metricPlotSeries_dict = {}
    if self.cursorPlotSeries_dict:
      for key in self.cursorPlotSeries_dict.keys():
        slicer.mrmlScene.RemoveNode(self.cursorPlotSeries_dict[key])
      self.cursorPlotSeries_dict = {}

    # Delete plot chart node
    if self.plotChartNode:
      slicer.mrmlScene.RemoveNode(self.plotChartNode)
      self.plotChartNode = None

  #------------------------------------------------------------------------------
  def allValuesEqual(self, iterable):
    """
    Returns True if all values in list are equal. False otherwise.
    """
    g = groupby(iterable)
    return next(g, True) and not next(g, False)

