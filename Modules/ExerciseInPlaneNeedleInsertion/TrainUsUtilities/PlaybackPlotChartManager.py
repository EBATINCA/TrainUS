from __main__ import vtk, slicer
import logging
from itertools import groupby

#------------------------------------------------------------------------------
#
# PlaybackPlotChartManager
#
#------------------------------------------------------------------------------
class PlaybackPlotChartManager:

  #------------------------------------------------------------------------------
  def __init__( self ):
    # Dictionary to store metric values
    self.metricData_dictionary = {}

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

  #------------------------------------------------------------------------------
  def getPlotChart(self):
    return self.plotChartNode

  #------------------------------------------------------------------------------
  def addNewMetric(self, metricName, metricValues):
    # Add new metric to dictionary
    self.metricData_dictionary[metricName] = list(metricValues)

    # Update list of metric names
    self.metricNames_list = self.getListOfMetrics()

  #------------------------------------------------------------------------------
  def getListOfMetrics(self):
    return list(self.metricData_dictionary.keys())

  #------------------------------------------------------------------------------
  def getNumberOfSamplesInMetric(self, metricName):
    metricValues = self.metricData_dictionary[metricName]
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

    # Add one column for each metric
    self.metricTableNode.SetLocked(True) # lock table to avoid modifications
    self.metricTableNode.RemoveAllColumns() # reset
    table = self.metricTableNode.GetTable()
    for metricID in range(numMetrics):
      array = vtk.vtkFloatArray()
      array.SetName(self.metricNames_list[metricID])
      table.AddColumn(array)

    # Fill table
    table.SetNumberOfRows(numSamples)
    for metricID in range(numMetrics):
      metricValues = self.metricData_dictionary[self.metricNames_list[metricID]]
      for sampleID in range(numSamples):
        table.SetValue(sampleID, metricID, metricValues[sampleID])
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

    # Add one column for each metric
    self.cursorTableNode.SetLocked(True) # lock table to avoid modifications
    self.cursorTableNode.RemoveAllColumns() # reset
    table = self.cursorTableNode.GetTable()
    for metricName in self.metricNames_list:
      array = vtk.vtkFloatArray()
      array.SetName(metricName)
      table.AddColumn(array)

    # Fill table
    table.SetNumberOfRows(1)
    for metricID in range(numMetrics):
      metricValues = self.metricData_dictionary[self.metricNames_list[metricID]]
      table.SetValue(0, metricID, max(metricValues[:]))
    table.Modified()

    # Set cursor to initial position
    self.updateCursorPosition(0)

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
      if (metricName != 'Sample ID') and (metricName != 'Timestamp'):
        plotSeriesNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLPlotSeriesNode')
        plotSeriesNode.SetName(metricName)
        plotSeriesNode.SetAndObserveTableNodeID(self.metricTableNode.GetID())
        plotSeriesNode.SetXColumnName('Sample ID')
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
      if (metricName != 'Sample ID') and (metricName != 'Timestamp'):
        plotSeriesNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLPlotSeriesNode')
        plotSeriesNode.SetName(metricName + '_Cursor')
        plotSeriesNode.SetAndObserveTableNodeID(self.cursorTableNode.GetID())
        plotSeriesNode.SetXColumnName('Sample ID')
        plotSeriesNode.SetYColumnName(metricName)
        plotSeriesNode.SetPlotType(slicer.vtkMRMLPlotSeriesNode.PlotTypeScatterBar)
        plotSeriesNode.SetMarkerStyle(slicer.vtkMRMLPlotSeriesNode.MarkerStyleCircle)
        plotSeriesNode.SetMarkerSize(plotMarkerSize)
        plotSeriesNode.SetLineWidth(plotLineWidth)
        plotSeriesNode.SetColor(plotColor)
        self.cursorPlotSeries_dict[metricName] = plotSeriesNode

  #------------------------------------------------------------------------------
  def createPlotChart(self):

    # Create metric table
    self.createMetricTable()

    # Create cursor table
    self.createCursorTable()

    # Create plot series
    self.createMetricPlotSeries()

    # Create cursor plot series
    self.createCursorPlotSeries()

    # Delete previous plot chart
    if self.plotChartNode:
      slicer.mrmlScene.RemoveNode(self.plotChartNode)
      self.plotChartNode = None

    # Create plot chart
    self.plotChartNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLPlotChartNode')
    self.plotChartNode.SetName('Chart')
    self.plotChartNode.RemoveAllPlotSeriesNodeIDs() # reset
    #self.plotChartNode.AddAndObservePlotSeriesNodeID(self.metricPlotSeries_dict[0].GetID())
    #self.plotChartNode.AddAndObservePlotSeriesNodeID(self.cursorPlotSeries_dict[0].GetID())
    self.plotChartNode.SetTitle('Metric Plot')
    self.plotChartNode.SetXAxisTitle('Sample ID')
    #self.plotChartNode.SetYAxisTitle('ANGLE (\xB0)')
    self.plotChartNode.SetAxisLabelFontSize(20)
    self.plotChartNode.LegendVisibilityOff() # hide legend
    self.plotChartNode.GridVisibilityOff()

    # Select first metric
    listOfMetrics = self.getListOfMetrics()
    for metricName in listOfMetrics:
      if (metricName != 'Sample ID') and (metricName != 'Timestamp'):
        self.plotChartNode.AddAndObservePlotSeriesNodeID(self.metricPlotSeries_dict[metricName].GetID())
        self.plotChartNode.AddAndObservePlotSeriesNodeID(self.cursorPlotSeries_dict[metricName].GetID())
        break

  #------------------------------------------------------------------------------
  def updatePlotChart(self, selectedMetricName):
    # Update visible plot series in plot chart
    if self.plotChartNode:
      self.plotChartNode.RemoveAllPlotSeriesNodeIDs() # reset
      self.plotChartNode.AddAndObservePlotSeriesNodeID(self.metricPlotSeries_dict[selectedMetricName].GetID())
      self.plotChartNode.AddAndObservePlotSeriesNodeID(self.cursorPlotSeries_dict[selectedMetricName].GetID())
      self.plotChartNode.SetTitle(selectedMetricName)

  #------------------------------------------------------------------------------
  def updateCursorPosition(self, itemID):
    if self.cursorTableNode:
      # Modify cursor table to force plot chart update
      table = self.cursorTableNode.GetTable()
      table.SetValue(0, 0, float(itemID))
      table.Modified()

  #------------------------------------------------------------------------------
  def allValuesEqual(self, iterable):
    """
    Returns True if all values in list are equal. False otherwise.
    """
    g = groupby(iterable)
    return next(g, True) and not next(g, False)

