import math
import vtk
from PythonMetricsCalculator import PerkEvaluatorMetric

class TargetsScanned( PerkEvaluatorMetric ):

  # A structure is "in" the imaging plane if it is within some small threshold of the plane
  IMAGE_PLANE_THRESHOLD = 5 #mm (since scaling should be uniform)


  # Static methods
  @staticmethod
  def GetMetricName():
    return "Targets Scanned"
  
  @staticmethod  
  def GetMetricUnit():
    return "%"
  
  @staticmethod
  def GetTransformRoles():
    return [ "Ultrasound" ]
  
  @staticmethod
  def GetAnatomyRoles():
    return { "POIs": "vtkMRMLMarkupsFiducialNode", "Image": "vtkMRMLVolumeNode" }
    
    
  # Instance methods    
  def __init__( self ):
    PerkEvaluatorMetric.__init__( self )
    
    self.imageMinX = 0
    self.imageMaxX = 0
    self.imageMinY = 0
    self.imageMaxY = 0
    
  def SetAnatomy( self, role, node ):   
    if ( role == "POIs" ):
      self.targets = node  
      self.hitTargets = [ 0 ] * self.targets.GetNumberOfFiducials()      
      return True
      
    if ( role == "Image" ):
      imageData = node.GetImageData()
      if ( imageData is None ):
        return False
      imageDimensions = [ 0, 0, 0 ]
      imageData.GetDimensions( imageDimensions )
      self.imageMaxX = imageDimensions[ 0 ]
      self.imageMaxY = imageDimensions[ 1 ]
      return True
      
    return False

    
  def AddTimestamp( self, time, matrix, point, role ):  
    for i in range( self.targets.GetNumberOfFiducials() ):    
      # Find the centre of the fiducial
      currTargetPosition = [ 0, 0, 0 ]
      self.targets.GetNthFiducialPosition( i, currTargetPosition )
      currTargetPosition_RAS = [ currTargetPosition[ 0 ], currTargetPosition[ 1 ], currTargetPosition[ 2 ], 1 ]
      
      # Assume the matrix is ImageToRAS
      # We know the center of mass of the structure in the RAS coordinate system
      # Transform the center of mass into the image coordinate system
      RASToImageMatrix = vtk.vtkMatrix4x4()
      RASToImageMatrix.DeepCopy( matrix )
      RASToImageMatrix.Invert()
    
      currTargetPosition_Image = [ 0, 0, 0, 1 ]
      RASToImageMatrix.MultiplyPoint( currTargetPosition_RAS, currTargetPosition_Image )
    
      # Assumption is the imaging plane is in the Image coordinate system's XY plane    
      if ( currTargetPosition_Image[0] < self.imageMinX or currTargetPosition_Image[0] > self.imageMaxX ):
        return
      
      if ( currTargetPosition_Image[1] < self.imageMinY or currTargetPosition_Image[1] > self.imageMaxY ):
        return
    
      # Note: This only works for similarity matrix (i.e. uniform scale factor)
      scaleFactor = math.pow( matrix.Determinant(), 1.0 / 3.0 )
    
      # Now check if the z-coordinate of the point in the image coordinate system is below some threshold value (i.e. 2mm)
      if ( abs( currTargetPosition_Image[2] ) < TargetsScanned.IMAGE_PLANE_THRESHOLD / scaleFactor ):
        self.hitTargets[ i ] = 1
    
    
  def GetMetric( self ):
    return 100 * float( sum( self.hitTargets ) ) / len( self.hitTargets )