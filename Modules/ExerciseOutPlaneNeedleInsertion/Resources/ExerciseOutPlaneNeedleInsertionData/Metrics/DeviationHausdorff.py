import math
import vtk
from PythonMetricsCalculator import PerkEvaluatorMetric

class DeviationHausdorff( PerkEvaluatorMetric ):

  # This metric computes the Hausdorff distance from the analyzed trajectory to a reference trajectory
  # AddTimestamp works in O( n ) time, where n is the number of points in the reference trajectory (which is fixed)

  # Static methods
  @staticmethod
  def GetMetricName():
    return "Deviation from Trajectory - Hausdorff"
    
  @staticmethod
  def GetMetricUnit():
    return "mm"
  
  @staticmethod  
  def GetAnatomyRoles():
    return { "Trajectory": "vtkMRMLSequenceNode" }
    
    
  # Instance methods  
  def __init__( self ):
    PerkEvaluatorMetric.__init__( self )
  
    self.hausdorffDistance = 0    
    self.trajectory = None
    
    
  def SetAnatomy( self, role, node ):
    if ( role == "Trajectory" ):
      self.trajectory = node    
      return True
      
    return False
    
  def AddTimestamp( self, time, matrix, point, role ):
    if ( self.trajectory is None ):
      return
    
    # Check distance from each point on the reference trajectory
    distances = [ 0 ] * self.trajectory.GetNumberOfDataNodes()
    for j in range( self.trajectory.GetNumberOfDataNodes() ):
      currTrajectoryNode = self.trajectory.GetNthDataNode( j )
      currTrajectoryMatrix = vtk.vtkMatrix4x4()
      currTrajectoryNode.GetMatrixTransformToWorld( currTrajectoryMatrix )
      currTrajectoryPoint = [ currTrajectoryMatrix.GetElement( 0, 3 ), currTrajectoryMatrix.GetElement( 1, 3 ), currTrajectoryMatrix.GetElement( 2, 3 ) ]
         
      distances[ j ] = vtk.vtkMath.Distance2BetweenPoints( point[ 0:3 ], currTrajectoryPoint )
          
    minDistance = math.sqrt( min( distances ) )
    self.hausdorffDistance = max( self.hausdorffDistance, minDistance )
    
  def GetMetric( self ):
    return self.hausdorffDistance