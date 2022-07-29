import math
import vtk
from PythonMetricsCalculator import PerkEvaluatorMetric

# Adapted from: Hofstad et al., A study of psychomotor skills in minimally invasive surgery: what differentiates expert and nonexpert performance, Surgical Endoscopy, 2013.
class BimanualDexterity( PerkEvaluatorMetric ):

  # Static methods
  @staticmethod
  def GetMetricName():
    return "Bimanual Dexterity: Translational & Rotational"
  
  @staticmethod  
  def GetMetricUnit():
    return "rho"
    
  @staticmethod
  def IsShared():
    return False
    
  @staticmethod
  def GetMetricShared():
    return False
  
  @staticmethod  
  def GetTransformRoles():
    return [ "LeftTool", "RightTool" ]
    


  # Instance methods  
  def __init__( self ):
    self.prevLeftInverseMatrix = None
    self.prevRightInverseMatrix = None
    self.prevLeftTime = None
    self.prevRightTime = None
    
    self.currLeftRotationalSpeed = None
    self.currRightRotationalSpeed = None
    self.currLeftTranslationalSpeed = None
    self.currRightTranslationalSpeed = None
    
    self.leftRotationalSumSquares = 0.0
    self.rightRotationalSumSquares = 0.0
    self.leftRotationalSum = 0.0
    self.rightRotationalSum = 0.0
    self.rotationalSumProducts = 0.0
    
    self.leftTranslationalSumSquares = 0.0
    self.rightTranslationalSumSquares = 0.0
    self.leftTranslationalSum = 0.0
    self.rightTranslationalSum = 0.0
    self.translationalSumProducts = 0.0
    
    self.leftCount = 0
    self.rightCount = 0
    self.totalCount = 0
    
    
  def AddAnatomyRole( self, role, node ):
    pass

    
  def AddTimestamp( self, time, matrix, point, role ):
    prevInverseMatrix = None
    if ( role == "LeftTool" ):
      prevInverseMatrix = self.prevLeftInverseMatrix 
    if ( role == "RightTool" ):
      prevInverseMatrix = self.prevRightInverseMatrix
    
    angle = None
    distance = None    
    if ( prevInverseMatrix is not None ):
      changeTransform = vtk.vtkTransform()
      changeTransform.Concatenate( matrix )
      changeTransform.Concatenate( prevInverseMatrix ) # matrix * prevInverseMatrix
      # Rotation
      axisAngle = [ 0, 0, 0, 0 ]
      changeTransform.GetOrientationWXYZ( axisAngle ) # This is in degrees
      angle = axisAngle[ 0 ]
      if ( angle > 180 ):
        angle = angle - 360
      # Translation
      position = [ 0, 0, 0 ]
      changeTransform.GetPosition( position )
      distance = vtk.vtkMath.Norm( position )
      
    if ( role == "LeftTool" ):
      if ( self.prevLeftTime is not None and angle is not None and distance is not None ):
        # Speeds
        self.currLeftRotationalSpeed = abs( angle / ( time - self.prevLeftTime ) )
        self.currLeftTranslationalSpeed = abs( distance / ( time - self.prevLeftTime ) )
        # Update the sums
        self.leftRotationalSum += self.currLeftRotationalSpeed
        self.leftRotationalSumSquares += self.currLeftRotationalSpeed * self.currLeftRotationalSpeed
        self.leftTranslationalSum += self.currLeftTranslationalSpeed
        self.leftTranslationalSumSquares += self.currLeftTranslationalSpeed * self.currLeftTranslationalSpeed
        # Increase count
        self.leftCount += 1
      # Update previous
      self.prevLeftTime = time
      self.prevLeftInverseMatrix = vtk.vtkMatrix4x4()
      self.prevLeftInverseMatrix.DeepCopy( matrix )
      self.prevLeftInverseMatrix.Invert()
      
    if ( role == "RightTool" ):
      if ( self.prevRightTime is not None and angle is not None and distance is not None ):
        # Speeds
        self.currRightRotationalSpeed = abs( angle / ( time - self.prevRightTime ) )
        self.currRightTranslationalSpeed = abs( distance / ( time - self.prevRightTime ) )
        # Update the sums
        self.rightRotationalSum += self.currRightRotationalSpeed
        self.rightRotationalSumSquares += self.currRightRotationalSpeed * self.currRightRotationalSpeed
        self.rightTranslationalSum += self.currRightTranslationalSpeed
        self.rightTranslationalSumSquares += self.currRightTranslationalSpeed * self.currRightTranslationalSpeed
        # Increase count
        self.rightCount += 1
      # Update previous
      self.prevRightTime = time
      self.prevRightInverseMatrix = vtk.vtkMatrix4x4()
      self.prevRightInverseMatrix.DeepCopy( matrix )
      self.prevRightInverseMatrix.Invert()
      
    if ( self.currLeftRotationalSpeed is None or self.currRightRotationalSpeed is None or self.currLeftTranslationalSpeed is None or self.currRightTranslationalSpeed is None ):
      return
      
    self.rotationalSumProducts +=  self.currLeftRotationalSpeed * self.rotationalSumProducts
    self.translationalSumProducts +=  self.currLeftTranslationalSpeed * self.currRightTranslationalSpeed
    self.totalCount += 1

       
  def GetMetric( self ):
    if ( self.totalCount == 0 or self.leftCount == 0 or self.rightCount == 0 ):
      return 0
    
    leftRotationalMean = self.leftRotationalSum / self.leftCount
    leftTranslationalMean = self.leftTranslationalSum / self.leftCount
    rightRotationalMean = self.rightRotationalSum / self.rightCount
    rightTranslationalMean = self.rightTranslationalSum / self.rightCount
    
    leftRotationalStdev = math.sqrt( self.leftRotationalSumSquares / self.leftCount - leftRotationalMean * leftRotationalMean )
    leftTranslationalStdev = math.sqrt( self.leftTranslationalSumSquares / self.leftCount - leftTranslationalMean * leftTranslationalMean )
    rightRotationalStdev = math.sqrt( self.rightRotationalSumSquares / self.rightCount - rightRotationalMean * rightRotationalMean )
    rightTranslationalStdev = math.sqrt( self.rightTranslationalSumSquares / self.rightCount - rightTranslationalMean * rightTranslationalMean )
    
    rotationalCovariance = self.rotationalSumProducts / self.totalCount - leftRotationalMean * rightRotationalMean
    translationalCovariance = self.translationalSumProducts / self.totalCount - leftTranslationalMean * rightTranslationalMean

    rotationalBimanualDexterity = rotationalCovariance / ( leftRotationalStdev * rightRotationalStdev )
    translationalBimanualDexterity = translationalCovariance / ( leftTranslationalStdev * rightTranslationalStdev )
    
    bimanualDexterity = [ translationalBimanualDexterity, rotationalBimanualDexterity ]
    separator = "\t"
    return separator.join( map( str, bimanualDexterity ) )