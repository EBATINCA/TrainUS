import math
import vtk
from PythonMetricsCalculator import PerkEvaluatorMetric

class RotationTotal( PerkEvaluatorMetric ):

  # Static methods
  @staticmethod
  def GetMetricName():
    return "Rotation Total"
  
  @staticmethod  
  def GetMetricUnit():
    return "deg"
    
    
  # Instance methods  
  def __init__( self ):
    PerkEvaluatorMetric.__init__( self )
  
    self.rotationTotal = 0
    self.matrixPrev = None
    
  def AddTimestamp( self, time, matrix, point, role ):  
    if ( self.matrixPrev == None or self.matrixPrev == None ):
      self.matrixPrev = vtk.vtkMatrix4x4()
      self.matrixPrev.DeepCopy( matrix )
      return
    
    invertPrev = vtk.vtkMatrix4x4()
    invertPrev.DeepCopy( self.matrixPrev )
    invertPrev.Invert()
    
    currChangeMatrix = vtk.vtkMatrix4x4()
    vtk.vtkMatrix4x4().Multiply4x4( matrix, invertPrev, currChangeMatrix )

    currChangeTransform = vtk.vtkTransform()
    currChangeTransform.SetMatrix( currChangeMatrix )
	
    angleChange = [ 0, 0, 0, 0 ]
    currChangeTransform.GetOrientationWXYZ( angleChange )

    currAngleChange = min( angleChange[ 0 ], 360 - angleChange[ 0 ] )
    self.rotationTotal += currAngleChange
	
    self.matrixPrev = vtk.vtkMatrix4x4()
    self.matrixPrev.DeepCopy( matrix )

    
  def GetMetric( self ):
    return self.rotationTotal