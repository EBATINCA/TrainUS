import math
import vtk
from PythonMetricsCalculator import PerkEvaluatorMetric

class DeviationTimeWarp( PerkEvaluatorMetric ):

  # This metric computes the average Dynamic Time Warping distance from the analyzed trajectory to a reference trajectory
  # Use dynamic programming to get this to work in "real-time"
  # AddTimestamp works in O( n ) time, where n is the number of points in the reference trajectory (which is fixed)
  # Inspired by: Despinoy, F., Zemiti, N., Forestier, G. et al. Int J CARS (2018) 13: 13. https://doi.org/10.1007/s11548-017-1666-6.
  # Divided by dtw path length: Sakoe, H., Chiba, S., IEEE Transactions on Acoustics, Speech, and Signal Processing, Volume: 26, Issue: 1, Feb 1978, Page(s): 43 - 49.

  # Static methods
  @staticmethod
  def GetMetricName():
    return "Deviation from Trajectory - Time Warp"
    
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
    self.dtwDistance = 0    
    self.trajectory = None
    
    self.dtwPathLength = 0
    self.pointPrev = None
    
    
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
         
      currDistance = math.sqrt( vtk.vtkMath.Distance2BetweenPoints( point[ 0:3 ], currTrajectoryPoint ) )
      if ( i == 0 ):
        if ( j == 0 ):
          self.distanceMatrix[ i ][ j ] = currDistance
        else:
          self.distanceMatrix[ i ][ j ] = currDistance + self.distanceMatrix[ i ][ j - 1 ]
      else:
        if ( j == 0 ):
          self.distanceMatrix[ i ][ j ] = currDistance + self.distanceMatrix[ i - 1 ][ j ]
        else:
          self.distanceMatrix[ i ][ j ] = currDistance + min( self.distanceMatrix[ i ][ j - 1 ], self.distanceMatrix[ i - 1 ][ j ], self.distanceMatrix[ i - 1 ][ j - 1 ] )
          
    self.dtwDistance = self.distanceMatrix[ i ][ self.trajectory.GetNumberOfDataNodes() - 1 ]
    
    # Assume the dtw path length is the sum of the number of points in each sequence minus 1
    # Note: this counts diagonal jumps as 2
    self.dtwPathLength = len( self.distanceMatrix ) + len( self.distanceMatrix[ i ] ) - 1
    
    
  def GetMetric( self ):
    if ( self.dtwPathLength != 0 ):
      return self.dtwDistance / self.dtwPathLength
    return 0