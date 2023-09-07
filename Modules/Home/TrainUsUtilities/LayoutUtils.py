from __main__ import vtk, slicer
import logging

#------------------------------------------------------------------------------
#
# LayoutUtils
#
#------------------------------------------------------------------------------
class LayoutUtils:

  #------------------------------------------------------------------------------
  def __init__( self ):
    # Current layout
    self.currentLayout = None

    # Previous layout
    self.lastLayout = None

    # Default layout
    self.defaultLayout = None

    # Layout IDs
    self.customLayout_Dual2D3D_ID = 999
    self.customLayout_Dual3D3D_ID = 1000
    self.customLayout_FourUp3D_ID = 1001
    self.customLayout_Dual2D3D_withPlot_ID = 1002
    self.customLayout_Dual2D3D_withTable_ID = 1003
    self.customLayout_TableOnly_ID = 1004
    self.customLayout_Dual3DTable_ID = 1005

    # Volume reslice driver (SlicerIGT extension)
    try:
      self.volumeResliceDriverLogic = slicer.modules.volumereslicedriver.logic()
    except:
      logging.error('ERROR: "Volume Reslice Driver" module was not found.')

    # Viewpoint module (SlicerIGT extension)
    try:
      import Viewpoint # Viewpoint Module must have been added to Slicer 
      self.viewpointLogic = Viewpoint.ViewpointLogic()
    except:
      logging.error('ERROR: "Viewpoint" module was not found.')

    # 3D view
    self.threeDViewNode = slicer.app.layoutManager().threeDWidget(0).mrmlViewNode()
    self.threeDView = slicer.app.layoutManager().threeDWidget(0).threeDView()

    # Register custom layouts
    self.registerCustomLayouts()

    # Slice controller visible by default
    self.updateSliceControllerVisibility(True)

  #------------------------------------------------------------------------------
  def getCurrentLayout(self):
    return self.currentLayout

  #------------------------------------------------------------------------------
  def getLastLayout(self):
    return self.lastLayout

  #------------------------------------------------------------------------------
  def getDefaultLayout(self):
    return self.defaultLayout

  #------------------------------------------------------------------------------
  def setDefaultLayout(self, layoutID):
    self.defaultLayout = layoutID

  #------------------------------------------------------------------------------
  def isPlotVisibleInCurrentLayout(self):
    if not self.currentLayout:
      return False
    layoutDescription = slicer.app.layoutManager().layoutLogic().GetLayoutNode().GetLayoutDescription(self.currentLayout)
    return ('vtkMRMLPlotViewNode' in layoutDescription)

  #------------------------------------------------------------------------------
  def isTableVisibleInCurrentLayout(self):
    if not self.currentLayout:
      return False
    layoutDescription = slicer.app.layoutManager().layoutLogic().GetLayoutNode().GetLayoutDescription(self.currentLayout)
    return ('vtkMRMLTableViewNode' in layoutDescription)

  #------------------------------------------------------------------------------
  def updateSliceControllerVisibility(self, visible):
    """
    Update visibility of slice controllers in slice views.
    """
    for name in slicer.app.layoutManager().sliceViewNames():
      sliceWidget = slicer.app.layoutManager().sliceWidget(name)
      sliceWidget.sliceController().setVisible(visible)

  #------------------------------------------------------------------------------
  def showViewerPinButton(self, sliceWidget, show):
    try:
      sliceControlWidget = sliceWidget.children()[1]
      pinButton = sliceControlWidget.children()[1].children()[1]
      if show:
        pinButton.show()
      else:
        pinButton.hide()
    except: # pylint: disable=w0702
      pass

  #------------------------------------------------------------------------------
  def setCustomLayout(self, layoutName):
    # Determine layout id from name
    if layoutName == '3D only':
      layoutID = slicer.vtkMRMLLayoutNode.SlicerLayoutOneUp3DView
    elif layoutName == '2D only red':
      layoutID = slicer.vtkMRMLLayoutNode.SlicerLayoutOneUpRedSliceView
    elif layoutName == '2D only yellow':
      layoutID = slicer.vtkMRMLLayoutNode.SlicerLayoutOneUpYellowSliceView
    elif layoutName == '2D only green':
      layoutID = slicer.vtkMRMLLayoutNode.SlicerLayoutOneUpGreenSliceView
    elif layoutName == '2D + 3D':
      layoutID = self.customLayout_Dual2D3D_ID
    elif layoutName == 'Dual 3D':
      layoutID = self.customLayout_Dual3D3D_ID
    elif layoutName == '2D + 3D + Plot':
      layoutID = self.customLayout_Dual2D3D_withPlot_ID
    elif layoutName == '2D + 3D + Table':
      layoutID = self.customLayout_Dual2D3D_withTable_ID
    elif layoutName == 'Four Up 3D':
      layoutID = self.customLayout_FourUp3D_ID
    elif layoutName == 'Plot only':
      layoutID = slicer.vtkMRMLLayoutNode.SlicerLayoutOneUpPlotView
    elif layoutName == 'Table only':
      layoutID = self.customLayout_TableOnly_ID
    elif layoutName == '3D + Table':
      layoutID = self.customLayout_Dual3DTable_ID
    else:
      layoutID = slicer.vtkMRMLLayoutNode.SlicerLayoutDefaultView

    # Update previous layout
    self.lastLayout = slicer.app.layoutManager().layout

    # Set layout
    slicer.app.layoutManager().setLayout(layoutID)

    # Update current layout
    self.currentLayout = slicer.app.layoutManager().layout    

  #------------------------------------------------------------------------------
  def restoreLastLayout(self):
    # Switch to last layout
    slicer.app.layoutManager().setLayout(self.lastLayout)

    # Update current layout
    self.currentLayout = slicer.app.layoutManager().layout

  #------------------------------------------------------------------------------
  def restoreDefaultLayout(self):
    # Switch to default layout
    slicer.app.layoutManager().setLayout(self.defaultLayout)

    # Update current layout
    self.currentLayout = slicer.app.layoutManager().layout

  #------------------------------------------------------------------------------
  def registerCustomLayouts(self):
    layoutManager= slicer.app.layoutManager()
    layoutLogic = layoutManager.layoutLogic()

    # Layout 2D (left) + 3D (right)
    customLayout_Dual2D3D = ("<layout type=\"horizontal\" split=\"true\">"
    " <item splitSize=\"400\" >\n"
    "  <view class=\"vtkMRMLSliceNode\" singletontag=\"Red\">"
    "     <property name=\"orientation\" action=\"default\">Axial</property>"
    "     <property name=\"viewlabel\" action=\"default\">R</property>"
    "     <property name=\"viewcolor\" action=\"default\">#F34A33</property>"
    "  </view>"
    " </item>"
    " <item splitSize=\"600\" >\n"
    "  <view class=\"vtkMRMLViewNode\" singletontag=\"1\">"
    "  <property name=\"viewlabel\" action=\"default\">T</property>"
    "  </view>"
    " </item>"
    "</layout>")
    
    # Layout 3D (left) + 3D (right)
    customLayout_Dual3D3D = ("<layout type=\"horizontal\" split=\"false\">"
    " <item>"
    "  <view class=\"vtkMRMLViewNode\" singletontag=\"1\">"
    "  <property name=\"viewlabel\" action=\"default\">1</property>"
    "  </view>"
    " </item>"
    " <item>"
    "  <view class=\"vtkMRMLViewNode\" singletontag=\"2\">"
    "  <property name=\"viewlabel\" action=\"default\">2</property>"
    "  </view>"
    " </item>"
    "</layout>")

    # Layout Four Up 3D
    customLayout_FourUp3D = ("<layout type=\"vertical\">"
    " <item>"
    "  <layout type=\"horizontal\">"
    "   <item>"
    "    <view class=\"vtkMRMLViewNode\" singletontag=\"1\">"
    "     <property name=\"viewlabel\" action=\"default\">1</property>"
    "    </view>"
    "   </item>"
    "   <item>"
    "    <view class=\"vtkMRMLViewNode\" singletontag=\"2\">"
    "     <property name=\"viewlabel\" action=\"default\">2</property>"
    "    </view>"
    "   </item>"
    "  </layout>"
    " </item>"
    " <item>"
    "  <layout type=\"horizontal\">"
    "   <item>"
    "    <view class=\"vtkMRMLViewNode\" singletontag=\"3\">"
    "     <property name=\"viewlabel\" action=\"default\">3</property>"
    "    </view>"
    "   </item>"
    "   <item>"
    "    <view class=\"vtkMRMLViewNode\" singletontag=\"4\">"
    "     <property name=\"viewlabel\" action=\"default\">4</property>"
    "    </view>"
    "   </item>"
    "  </layout>"
    " </item>"
    "</layout>")

    # Layout 2D (top left) + 3D (top right) + Plot (bottom)
    customLayout_Dual2D3D_withPlot = ("<layout type=\"vertical\" split=\"true\" >\n"
    " <item splitSize=\"700\" >\n"
    "  <layout type=\"horizontal\" split=\"true\">"
    "   <item>"
    "    <view class=\"vtkMRMLSliceNode\" singletontag=\"Red\">"
    "       <property name=\"orientation\" action=\"default\">Axial</property>"
    "       <property name=\"viewlabel\" action=\"default\">R</property>"
    "       <property name=\"viewcolor\" action=\"default\">#F34A33</property>"
    "    </view>"
    "   </item>"
    "   <item>"
    "    <view class=\"vtkMRMLViewNode\" singletontag=\"1\">"
    "    <property name=\"viewlabel\" action=\"default\">T</property>"
    "    </view>"
    "   </item>"
    "  </layout>"
    " </item>"
    " <item splitSize=\"300\" >\n"
    "  <view class=\"vtkMRMLPlotViewNode\" singletontag=\"PlotView1\">"
    "  <property name=\"viewlabel\" action=\"default\">1</property>"
    "  </view>"
    " </item>"
    "</layout>")

    # Layout 2D (top left) + 3D (top right) + Table (bottom)
    customLayout_Dual2D3D_withTable = ("<layout type=\"vertical\" split=\"true\" >\n"
    " <item splitSize=\"700\" >\n"
    "  <layout type=\"horizontal\" split=\"true\">"
    "   <item>"
    "    <view class=\"vtkMRMLSliceNode\" singletontag=\"Red\">"
    "       <property name=\"orientation\" action=\"default\">Axial</property>"
    "       <property name=\"viewlabel\" action=\"default\">R</property>"
    "       <property name=\"viewcolor\" action=\"default\">#F34A33</property>"
    "    </view>"
    "   </item>"
    "   <item>"
    "    <view class=\"vtkMRMLViewNode\" singletontag=\"1\">"
    "    <property name=\"viewlabel\" action=\"default\">T</property>"
    "    </view>"
    "   </item>"
    "  </layout>"
    " </item>"
    " <item splitSize=\"300\" >\n"
    "  <view class=\"vtkMRMLTableViewNode\" singletontag=\"TableView1\">"
    "  <property name=\"viewlabel\" action=\"default\">T</property>"
    "  </view>"
    " </item>"
    "</layout>")

    # Layout table only
    customLayout_TableOnly = ("<layout type=\"horizontal\">"
    " <item>"
    "  <view class=\"vtkMRMLTableViewNode\" singletontag=\"TableView1\">"
    "  <property name=\"viewlabel\" action=\"default\">T</property>"
    "  </view>"
    " </item>"
    "</layout>")

    # Layout 3D (left) + Table (right)
    customLayout_Dual3DTable = ("<layout type=\"horizontal\" split=\"true\" >\n"
    " <item splitSize=\"500\" >\n"
    "  <view class=\"vtkMRMLViewNode\" singletontag=\"1\">"
    "  <property name=\"viewlabel\" action=\"default\">T</property>"
    "  </view>"
    " </item>"
    " <item splitSize=\"500\" >\n"
    "  <view class=\"vtkMRMLTableViewNode\" singletontag=\"TableView1\">"
    "  <property name=\"viewlabel\" action=\"default\">T</property>"
    "  </view>"
    " </item>"
    "</layout>")    

    # Register custom layouts
    layoutLogic.GetLayoutNode().AddLayoutDescription(self.customLayout_Dual2D3D_ID, customLayout_Dual2D3D)
    layoutLogic.GetLayoutNode().AddLayoutDescription(self.customLayout_Dual3D3D_ID, customLayout_Dual3D3D)
    layoutLogic.GetLayoutNode().AddLayoutDescription(self.customLayout_FourUp3D_ID, customLayout_FourUp3D)
    layoutLogic.GetLayoutNode().AddLayoutDescription(self.customLayout_Dual2D3D_withPlot_ID, customLayout_Dual2D3D_withPlot)
    layoutLogic.GetLayoutNode().AddLayoutDescription(self.customLayout_Dual2D3D_withTable_ID, customLayout_Dual2D3D_withTable)
    layoutLogic.GetLayoutNode().AddLayoutDescription(self.customLayout_TableOnly_ID, customLayout_TableOnly)
    layoutLogic.GetLayoutNode().AddLayoutDescription(self.customLayout_Dual3DTable_ID, customLayout_Dual3DTable)

  #------------------------------------------------------------------------------
  def showUltrasoundInSliceView(self, ultrasoundVolumeNode, sliceViewName):
    # Get slice logic
    sliceLogic = slicer.app.layoutManager().sliceWidget(sliceViewName).sliceLogic()

    """
    # Make all slice nodes invisible in 3D views except for ultrasound image
    volumeNodesInScene = slicer.mrmlScene.GetNodesByClass('vtkMRMLScalarVolumeNode')
    for volumeNode in volumeNodesInScene:
      sliceLogic.GetSliceCompositeNode().SetBackgroundVolumeID(volumeNode.GetID())
      sliceLogic.GetSliceNode().SetSliceVisible(False)
    """
      
    # Select background volume in slice view
    sliceLogic.GetSliceCompositeNode().SetBackgroundVolumeID(ultrasoundVolumeNode.GetID())

    # Activate volume reslice driver
    self.volumeResliceDriverLogic.SetDriverForSlice(ultrasoundVolumeNode.GetID(), sliceLogic.GetSliceNode())
    self.volumeResliceDriverLogic.SetModeForSlice(self.volumeResliceDriverLogic.MODE_TRANSVERSE, sliceLogic.GetSliceNode())

    # Fit US image to view    
    sliceLogic.FitSliceToAll()

    # Do not link slice view control
    sliceLogic.GetSliceCompositeNode().SetLinkedControl(False)

    # Display image in 3D view
    sliceLogic.GetSliceNode().SetSliceVisible(True)

  #------------------------------------------------------------------------------
  def showImageInstructionsInSliceView(self, instructionsVolumeNode, sliceViewName):
    # Get slice widget
    sliceWidget = slicer.app.layoutManager().sliceWidget(sliceViewName)

    # Get slice logic
    sliceLogic = sliceWidget.sliceLogic()

    # Select background volume in slice view
    sliceLogic.GetSliceCompositeNode().SetBackgroundVolumeID(instructionsVolumeNode.GetID())

    # Deactivate volume reslice driver
    self.volumeResliceDriverLogic.SetModeForSlice(self.volumeResliceDriverLogic.MODE_NONE, sliceLogic.GetSliceNode())

    # Set slice properties
    sliceLogic.GetSliceNode().SetOrientationToAxial()
    sliceLogic.FitSliceToAll()
    sliceLogic.SetSliceOffset(0)

    # Do not link slice view control
    sliceLogic.GetSliceCompositeNode().SetLinkedControl(False)

    # Do not display in 3D view
    sliceLogic.GetSliceNode().SetSliceVisible(False)

    # Disable slice widget to avoid mouse interactions (drag, zoom, ...)
    #sliceWidget.enabled = False

  #------------------------------------------------------------------------------
  def showVideoInstructionsInSliceView(self, instructionsVolumeNode, sliceViewName):
    # Get slice widget
    sliceWidget = slicer.app.layoutManager().sliceWidget(sliceViewName)

    # Get slice logic
    sliceLogic = sliceWidget.sliceLogic()

    # Select background volume in slice view
    sliceLogic.GetSliceCompositeNode().SetBackgroundVolumeID(instructionsVolumeNode.GetID())

    # Deactivate volume reslice driver
    self.volumeResliceDriverLogic.SetModeForSlice(self.volumeResliceDriverLogic.MODE_NONE, sliceLogic.GetSliceNode())

    # Set slice properties
    sliceLogic.GetSliceNode().SetOrientationToAxial()
    sliceLogic.FitSliceToAll()
    sliceLogic.SetSliceOffset(0)

    # Do not link slice view control
    sliceLogic.GetSliceCompositeNode().SetLinkedControl(False)

    # Do not display in 3D view
    sliceLogic.GetSliceNode().SetSliceVisible(False)

    # Disable slice widget to avoid mouse interactions (drag, zoom, ...)
    #sliceWidget.enabled = False

  #------------------------------------------------------------------------------
  def previousInstructionInSliceView(self, sliceViewName):
    # Get slice logic
    sliceLogic = slicer.app.layoutManager().sliceWidget(sliceViewName).sliceLogic()

    # Modify slice offset
    sliceOffset = sliceLogic.GetSliceOffset()
    sliceIndex = sliceLogic.GetSliceIndexFromOffset(sliceOffset - 1)
    if sliceIndex > 0:
      sliceLogic.SetSliceOffset(sliceOffset - 1)

  #------------------------------------------------------------------------------
  def nextInstructionInSliceView(self, sliceViewName):
    # Get slice logic
    sliceLogic = slicer.app.layoutManager().sliceWidget(sliceViewName).sliceLogic()

    # Modify slice offset
    sliceOffset = sliceLogic.GetSliceOffset()
    sliceIndex = sliceLogic.GetSliceIndexFromOffset(sliceOffset + 1)
    if sliceIndex > 0:
      sliceLogic.SetSliceOffset(sliceOffset + 1)

  #------------------------------------------------------------------------------
  def get3DViewNode(self):
    threeDViewNode = slicer.app.layoutManager().threeDWidget(0).mrmlViewNode()
    return threeDViewNode

  #------------------------------------------------------------------------------
  def resetFocalPointInThreeDView(self):
    threeDView = slicer.app.layoutManager().threeDWidget(0).threeDView()
    threeDView.resetFocalPoint()

  #------------------------------------------------------------------------------
  def hideCubeAndLabelsInThreeDView(self):
    threeDViewNode = self.get3DViewNode()
    threeDViewNode.SetBoxVisible(False)
    threeDViewNode.SetAxisLabelsVisible(False)

  #------------------------------------------------------------------------------
  def activateViewpoint(self, cameraTransform):
    # Get 3D view node
    threeDViewNode = self.get3DViewNode()

    # Disable bulleye mode if active
    bullseyeMode = self.viewpointLogic.getViewpointForViewNode(threeDViewNode).getCurrentMode()
    if bullseyeMode:
      self.viewpointLogic.getViewpointForViewNode(threeDViewNode).bullseyeStop()
    
    # Update viewpoint
    if cameraTransform:
      self.viewpointLogic.getViewpointForViewNode(threeDViewNode).setViewNode(threeDViewNode)
      self.viewpointLogic.getViewpointForViewNode(threeDViewNode).bullseyeSetTransformNode(cameraTransform)
      self.viewpointLogic.getViewpointForViewNode(threeDViewNode).bullseyeStart()  

  #------------------------------------------------------------------------------
  def setActivePlotChart(self, plotChartNode):
    """
    Show input plot chart node in plot view
    """
    if plotChartNode:
      slicer.app.applicationLogic().GetSelectionNode().SetReferenceActivePlotChartID(plotChartNode.GetID())
      slicer.app.applicationLogic().PropagatePlotChartSelection()

  #------------------------------------------------------------------------------
  def setActiveTable(self, tableNode):
    """
    Show input table node in table view
    """
    if tableNode:
      slicer.app.applicationLogic().GetSelectionNode().SetReferenceActiveTableID(tableNode.GetID())
      slicer.app.applicationLogic().PropagateTableSelection()
