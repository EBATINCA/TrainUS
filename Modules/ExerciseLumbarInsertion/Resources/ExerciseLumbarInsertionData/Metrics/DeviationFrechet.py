import math
import vtk
from PythonMetricsCalculator import PerkEvaluatorMetric

class DeviationFrechet( PerkEvaluatorMetric ):

  # This metric computes the Frechet distance from the analyzed trajectory to a reference trajectory
  # Use dynamic programming to get this to work in "real-time"
  # AddTimestamp works in O( n ) time, where n is the number of points in the reference trajectory (which is fixed)
  # Based on: Eiter, Thomas; Mannila, Heikki (1994), Computing discrete Fréchet distance (PDF), Tech. Report CD-TR 94/64, Christian Doppler Laboratory for Expert Systems, TU Vienna, Austria.

  # Static methods
  @staticmethod
  def GetMetricName():
    return "Deviation from Trajectory - Frechet"
    
  @staticmethod
  def GetMetricUnit():
    return "mm"
  
  @staticmethod  
  def GetAnatomyRoles():
    return { "Trajectory": "vtkMRMLSequenceNode" }
    
    
  # Instance methods  
  def __init__( self ):
    PerkEvaluatorMetric.__init__( self )
  
    self.distanceMatrix = []
    self.frechetDistance = 0    
    self.trajectory = None
    
    
  def SetAnatomy( self, role, node ):
    if ( role == "Trajectory" ):
      self.trajectory = node    
      return True
      
    return False
    
  def AddTimestamp( self, time, matrix, point, role ):
    if ( self.trajectory is None ):
      return
      
    # Build up the matrix
    newRow = [ 0 ] * self.trajectory.GetNumberOfDataNodes()
    self.distanceMatrix.append( newRow )
    i = len( self.distanceMatrix ) - 1
    
    # Use dynamic programming to compute the next row
    for j in range( self.trajectory.GetNumberOfDataNodes() ):
      currTrajectoryNode = self.trajectory.GetNthDataNode( j )
      currTrajectoryMatrix = vtk.vtkMatrix4x4()
      currTrajectoryNode.GetMatrixTransformToWorld( currTrajectoryMatrix )
      currTrajectoryPoint = [ currTrajectoryMatrix.GetElement( 0, 3 ), currTrajectoryMatrix.GetElement( 1, 3 ), currTrajectoryMatrix.GetElement( 2, 3 ) ]
         
      currDistance = vtk.vtkMath.Distance2BetweenPoints( point[ 0:3 ], currTrajectoryPoint )
      if ( i == 0 ):
        if ( j == 0 ):
          self.distanceMatrix[ i ][ j ] = currDistance
        else:
          self.distanceMatrix[ i ][ j ] = max( self.distanceMatrix[ i ][ j - 1 ], currDistance )
      else:
        if ( j == 0 ):
          self.distanceMatrix[ i ][ j ] = max( self.distanceMatrix[ i - 1 ][ j ], currDistance )
        else:
          self.distanceMatrix[ i ][ j ] = max( min( self.distanceMatrix[ i ][ j - 1 ], self.distanceMatrix[ i - 1 ][ j ], self.distanceMatrix[ i - 1 ][ j - 1 ] ), currDistance )
          
    self.frechetDistance = math.sqrt( self.distanceMatrix[ i ][ self.trajectory.GetNumberOfDataNodes() - 1 ] )
    
  def GetMetric( self ):
    return self.frechetDistance