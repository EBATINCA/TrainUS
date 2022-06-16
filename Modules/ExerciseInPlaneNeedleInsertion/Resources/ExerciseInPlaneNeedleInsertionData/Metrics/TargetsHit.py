import math
import vtk
from PythonMetricsCalculator import PerkEvaluatorMetric

class TargetsHit( PerkEvaluatorMetric ):

  # A target is "hit" if the needle tip is within this threshold of the target point
  TARGET_THRESHOLD = 3 #mm


  # Static methods
  @staticmethod
  def GetMetricName():
    return "Targets Hit"
  
  @staticmethod  
  def GetMetricUnit():
    return "count"
  
  @staticmethod
  def GetTransformRoles():
    return [ "Needle" ]
  
  @staticmethod
  def GetAnatomyRoles():
    return { "Targets": "vtkMRMLMarkupsFiducialNode" }
    
    
  # Instance methods    
  def __init__( self ):
    PerkEvaluatorMetric.__init__( self )

    
  def SetAnatomy( self, role, node ):   
    if ( role == "Targets" ):
      self.targets = node  
      self.hitTargets = [ 0 ] * self.targets.GetNumberOfFiducials()      
      return True
      
    return False

    
  def AddTimestamp( self, time, matrix, point, role ):  
    for i in range( self.targets.GetNumberOfFiducials() ):    
      # Find the centre of the fiducial
      currTargetPosition = [ 0, 0, 0 ]
      self.targets.GetNthFiducialPosition( i, currTargetPosition )
      currTargetPosition_RAS = [ currTargetPosition[ 0 ], currTargetPosition[ 1 ], currTargetPosition[ 2 ] ]
      
      # Find the needle tip in RAS
      needleTip_RAS = point[0:3]
      
      needleTipTargetDistance = math.sqrt( vtk.vtkMath.Distance2BetweenPoints( currTargetPosition_RAS, needleTip_RAS ) )
      
      if ( needleTipTargetDistance < TargetsHit.TARGET_THRESHOLD ):
        self.hitTargets[ i ] = 1
    
    
  def GetMetric( self ):
    return sum( self.hitTargets )