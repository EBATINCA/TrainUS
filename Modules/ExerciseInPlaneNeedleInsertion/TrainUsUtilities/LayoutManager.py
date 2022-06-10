from __main__ import vtk, slicer
import logging

#------------------------------------------------------------------------------
#
# LayoutManager
#
#------------------------------------------------------------------------------
class LayoutManager:

  #------------------------------------------------------------------------------
  def __init__( self ):
    # Current layout
    self.currentLayout = None

    # Previous layout
    self.lastLayout = None

    # Layout IDs
    self.customLayout_Dual2D3D_ID = 997
    self.customLayout_2Donly_red_ID = 998
    self.customLayout_2Donly_yellow_ID = 999
    self.customLayout_Dual3D3D_ID = 1000
    self.customLayout_FourUp3D_ID = 1001
    self.customLayout_Dual2D3D_withPlot_ID = 1002

    # Volume reslice driver (SlicerIGT extension)
    try:
      self.volumeResliceDriverLogic = slicer.modules.volumereslicedriver.logic()
    except:
      logging.error('ERROR: "Volume Reslice Driver" module was not found.')

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
      layoutID = self.customLayout_2Donly_red_ID
    elif layoutName == '2D only yellow':
      layoutID = self.customLayout_2Donly_yellow_ID
    elif layoutName == '2D + 3D':
      layoutID = self.customLayout_Dual2D3D_ID
    elif layoutName == 'Dual 3D':
      layoutID = self.customLayout_Dual3D3D_ID
    elif layoutName == '2D + 3D + Plot':
      layoutID = self.customLayout_Dual2D3D_withPlot_ID
    elif layoutName == 'Four Up 3D':
      layoutID = self.customLayout_FourUp3D_ID
    elif layoutName == 'Plot only':
      layoutID = slicer.vtkMRMLLayoutNode.SlicerLayoutOneUpPlotView
    else:
      layoutID = 1

    # Store previous layout
    self.lastLayout = slicer.app.layoutManager().layout

    # Set layout
    slicer.app.layoutManager().setLayout(layoutID)

    # Store current layout
    self.currentLayout = slicer.app.layoutManager().layout    

  #------------------------------------------------------------------------------
  def restoreLastLayout(self):
    slicer.app.layoutManager().setLayout(self.lastLayout)

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

    # Layout 2D only (red view)
    customLayout_2Donly_red = ("<layout type=\"horizontal\">"
    " <item>"
    "  <view class=\"vtkMRMLSliceNode\" singletontag=\"Red\">"
    "   <property name=\"orientation\" action=\"default\">Axial</property>"
    "     <property name=\"viewlabel\" action=\"default\">R</property>"
    "     <property name=\"viewcolor\" action=\"default\">#F34A33</property>"
    "  </view>"
    " </item>"
    "</layout>")

    # Layout 2D only (yellow view)
    customLayout_2Donly_yellow = ("<layout type=\"horizontal\">"
    " <item>"
    "  <view class=\"vtkMRMLSliceNode\" singletontag=\"Yellow\">"
    "   <property name=\"orientation\" action=\"default\">Axial</property>"
    "     <property name=\"viewlabel\" action=\"default\">Y</property>"
    "     <property name=\"viewcolor\" action=\"default\">#F34A33</property>"
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
    customLayout_Dual2D3DwithPlot = ("<layout type=\"vertical\" split=\"true\" >\n"
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

    # Register custom layouts
    layoutLogic.GetLayoutNode().AddLayoutDescription(self.customLayout_Dual2D3D_ID, customLayout_Dual2D3D)
    layoutLogic.GetLayoutNode().AddLayoutDescription(self.customLayout_2Donly_red_ID, customLayout_2Donly_red)
    layoutLogic.GetLayoutNode().AddLayoutDescription(self.customLayout_2Donly_yellow_ID, customLayout_2Donly_yellow)
    layoutLogic.GetLayoutNode().AddLayoutDescription(self.customLayout_Dual3D3D_ID, customLayout_Dual3D3D)
    layoutLogic.GetLayoutNode().AddLayoutDescription(self.customLayout_FourUp3D_ID, customLayout_FourUp3D)
    layoutLogic.GetLayoutNode().AddLayoutDescription(self.customLayout_Dual2D3D_withPlot_ID, customLayout_Dual2D3DwithPlot)

  #------------------------------------------------------------------------------
  def showUltrasoundInSliceView(self, ultrasoundVolumeNode, sliceViewName):
    # Get slice logic
    sliceLogic = slicer.app.layoutManager().sliceWidget(sliceViewName).sliceLogic()

    # Select background volume in slice view
    sliceLogic.GetSliceCompositeNode().SetBackgroundVolumeID(ultrasoundVolumeNode.GetID())

    # Activate volume reslice driver
    self.volumeResliceDriverLogic.SetDriverForSlice(ultrasoundVolumeNode.GetID(), sliceLogic.GetSliceNode())
    self.volumeResliceDriverLogic.SetModeForSlice(self.volumeResliceDriverLogic.MODE_TRANSVERSE, sliceLogic.GetSliceNode())

    # Fit US image to view    
    sliceLogic.FitSliceToAll()

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

    # Disable slice widget to avoid mouse interactions (drag, zoom, ...)
    sliceWidget.enabled = False

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
    threeDViewNode = slicer.app.layoutManager().threeDWidget(0).mrmlViewNode()
    threeDViewNode.SetBoxVisible(False)
    threeDViewNode.SetAxisLabelsVisible(False)

  
