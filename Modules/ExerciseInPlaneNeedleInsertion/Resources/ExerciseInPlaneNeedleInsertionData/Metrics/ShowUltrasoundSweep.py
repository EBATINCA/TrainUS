import math
import vtk
from PythonMetricsCalculator import PerkEvaluatorMetric

class ShowUltrasoundSweep( PerkEvaluatorMetric ):

  # Static methods
  @staticmethod
  def GetMetricName():
    return "Display Ultrasound Sweep"
  
  @staticmethod  
  def GetMetricUnit():
    return ""
  
  @staticmethod
  def GetTransformRoles():
    return [ "Ultrasound" ]
    
  @staticmethod
  def GetAnatomyRoles():
    return { "OutputModel": "vtkMRMLModelNode", "Image": "vtkMRMLVolumeNode" }
    
    
  # Instance methods  
  def __init__( self ):
    PerkEvaluatorMetric.__init__( self )
    
    self.outputPolyData = vtk.vtkAppendPolyData()
    
    self.planeSource = vtk.vtkPlaneSource()
    self.planePolyData = self.planeSource.GetOutput()
    
    
  def SetAnatomy( self, role, node ):   
    if ( role == "OutputModel" ):
      node.SetAndObservePolyData( self.outputPolyData.GetOutput() )
      if ( node.GetModelDisplayNode() is None ):
        node.CreateDefaultDisplayNodes()
      modelDisplayNode = node.GetModelDisplayNode()
      modelDisplayNode.FrontfaceCullingOff()
      modelDisplayNode.BackfaceCullingOff() 
      return True
      
    if ( role == "Image" ):
      imageData = node.GetImageData()
      if ( imageData is None ):
        return False
      imageDimensions = [ 0, 0, 0 ]
      imageData.GetDimensions( imageDimensions )
      self.planeSource.SetOrigin( 0, 0, 0 )
      self.planeSource.SetPoint1( imageDimensions[ 0 ], 0, 0 )
      self.planeSource.SetPoint2( 0, imageDimensions[ 1 ], 0 )
      self.planeSource.Update()
      return True

    return False
    
  def AddTimestamp( self, time, matrix, point, role ):  
    worldTransform = vtk.vtkTransform()
    worldTransform.SetMatrix( matrix )
  
    planeSweepTransformPolyData = vtk.vtkTransformPolyDataFilter()
    planeSweepTransformPolyData.SetTransform( worldTransform )
    planeSweepTransformPolyData.SetInputData( self.planePolyData )
    planeSweepTransformPolyData.Update()
  
    self.outputPolyData.AddInputData( planeSweepTransformPolyData.GetOutput() )
    self.outputPolyData.Update()