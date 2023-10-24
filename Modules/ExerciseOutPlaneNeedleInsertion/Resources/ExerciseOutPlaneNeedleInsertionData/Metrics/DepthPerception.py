import math
import vtk
from PythonMetricsCalculator import PerkEvaluatorMetric

class DepthPerception( PerkEvaluatorMetric ):

  # Static methods
  @staticmethod
  def GetMetricName():
    return "Depth Perception"
  
  @staticmethod  
  def GetMetricUnit():
    return "mm"
    
  @staticmethod
  def GetTransformRoles():
    return [ "Needle" ]
    
    
  # Instance methods  
  def __init__( self ):
    PerkEvaluatorMetric.__init__( self )
    
    self.depthPerception = 0 
    self.pointPrev = None    
    
  def AddTimestamp( self, time, matrix, point, role ):
    if ( self.pointPrev == None ):
      self.pointPrev = point[:]
      
    # Find the prev to current vector
    prevToCurrentVector = [ 0, 0, 0 ]
    vtk.vtkMath().Subtract( point[0:3], self.pointPrev[0:3], prevToCurrentVector )
    prevToCurrentVector = [ prevToCurrentVector[ 0 ], prevToCurrentVector[ 1 ], prevToCurrentVector[ 2 ] ]
    
    # Compute the direction vector of the needle in RAS, using the needle orientation protocol
    needleOrientation = self.NeedleOrientation[:]
    needleOrientation.append( 0 )
    needleVector_RAS = [ 0, 0, 0, 0 ]
    matrix.MultiplyPoint( needleOrientation, needleVector_RAS )
    
    # Find the movement in the needle direction
    needleAxisMovement = vtk.vtkMath().Dot( prevToCurrentVector, needleVector_RAS[ 0:3 ] )
    
    self.depthPerception += math.fabs( needleAxisMovement )
    
    self.pointPrev = point[:]
        
  def GetMetric( self ):
    return self.depthPerception