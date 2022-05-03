import math
import vtk

class PerkEvaluatorMetric:

  # Note: An action is defined as a time period where the absolute velocity of motion is greater than some threshold
  TRANSLATIONAL_VELOCITY_THRESHOLD = 5 #mm/s
  ROTATIONAL_VELOCITY_THRESHOLD = 10 #deg/s
  TIME_THRESHOLD = 0.2 #s


  # Static methods
  @staticmethod
  def GetMetricName():
    return "In Action"
  
  @staticmethod  
  def GetMetricUnit():
    return "true/false"
  
  @staticmethod  
  def GetAcceptedTransformRoles():
    return [ "Needle" ]
  
  @staticmethod  
  def GetRequiredAnatomyRoles():
    return { "Parameter": "vtkMRMLNode" }
    
  @staticmethod  
  def IsHidden():
    return True
    
    
  # Instance methods  
  def __init__( self ):   
    self.actionState = False
    self.completeActionTime = 0
    
    self.timePrev = None
    self.matrixPrev = None
    
    self.outputParameterNode = None
    
  def AddAnatomyRole( self, role, node ):
    if ( node == None or not node.IsA( self.GetRequiredAnatomyRoles()[ role ] ) ):
      return False
      
    if ( role == "Parameter" ):
      self.outputParameterNode = node
      return True
      
    return False
    
  def AddTimestamp( self, time, matrix, point ):
  
    if ( time == self.timePrev ):
      return
    
    if ( self.timePrev == None or self.matrixPrev == None ):
      self.timePrev = time
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
    
    
    ## Translational velocity
    currTranslationalVelocity = [ 0, 0, 0 ]
    currChangeTransform.GetPosition( currTranslationalVelocity )
    currAbsTranslationalVelocity = vtk.vtkMath.Norm( currTranslationalVelocity )
    currAbsTranslationalVelocity = currAbsTranslationalVelocity / ( time - self.timePrev )
    
    
    ## Angular velocity
    currRotationalVelocity = [ 0, 0, 0, 0 ]
    currChangeTransform.GetOrientationWXYZ( currRotationalVelocity )
    currRotationalVelocity = currRotationalVelocity[ 0 ]
    # Make the range -180 to 180
    if ( currRotationalVelocity > 180 ):
      currRotationalVelocity = currRotationalVelocity - 360
    currAbsRotationalVelocity = abs( currRotationalVelocity )
    currAbsRotationalVelocity = currAbsRotationalVelocity / ( time - self.timePrev )
      

    ## Compute the current action state
    currentTestState = ( currAbsTranslationalVelocity > PerkEvaluatorMetric.TRANSLATIONAL_VELOCITY_THRESHOLD )
    # or ( currAbsRotationalVelocity > PerkEvaluatorMetric.ROTATIONAL_VELOCITY_THRESHOLD ) # We may not care about rotation
    
    if ( currentTestState == self.actionState ):
      self.completeActionTime = time
    else:
      if ( ( time - self.completeActionTime ) > PerkEvaluatorMetric.TIME_THRESHOLD ):
        self.actionState = currentTestState
        self.completeActionTime = time
        
        
    ## Output the result to the output parameter node
    self.outputParameterNode.SetAttribute( "PerkTutor_InAction", str( self.actionState ) )  
        
    self.timePrev = time
    self.matrixPrev = vtk.vtkMatrix4x4()
    self.matrixPrev.DeepCopy( matrix )

  def GetMetric( self ):
    return self.actionState