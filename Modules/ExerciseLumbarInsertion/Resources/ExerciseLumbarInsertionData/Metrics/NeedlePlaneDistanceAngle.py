import math
import vtk

class PerkEvaluatorMetric:

  @staticmethod
  def GetMetricName():
    return "Needle Plane Distance | Angle"

  @staticmethod
  def GetMetricUnit():
    return "mm | deg"

  @staticmethod
  def GetAcceptedTransformRoles():
    return [ "Needle", "Ultrasound" ]

  @staticmethod
  def GetRequiredAnatomyRoles():
    # Use a parameter node to pass the computed values to other metrics
    return { "Parameter": "vtkMRMLNode" }
    
  @staticmethod  
  def IsHidden():
    return True
    

  def __init__( self ):
    self.outputParameterNode = None
    
    self.needleTipToWorldMatrix = None
    self.ultrasoundToWorldMatrix = None
    
    self.currDistanceMm = 0
    self.currAngleDeg = 0

  def AddAnatomyRole( self, role, node ):
    if ( node == None or not node.IsA( self.GetRequiredAnatomyRoles()[ role ] ) ):
      return False
      
    if ( role == "Parameter" ):
      self.outputParameterNode = node
      return True

    return False

  def AddTimestamp( self, time, matrix, point, role ):
    if ( role == "Needle" ):
      self.needleTipToWorldMatrix = matrix
      
    if ( role == "Ultrasound" ):
      self.ultrasoundToWorldMatrix = matrix

    if ( self.needleTipToWorldMatrix == None or self.ultrasoundToWorldMatrix == None ):
      return
    
    
    # Calculate the NeedleTipToUltrasoundMatrix
    worldToUltrasoundMatrix = vtk.vtkMatrix4x4()
    worldToUltrasoundMatrix.DeepCopy( self.ultrasoundToWorldMatrix )
    worldToUltrasoundMatrix.Invert()
    
    needleTipToUltrasoundTransform = vtk.vtkTransform()
    needleTipToUltrasoundTransform.Identity()
    needleTipToUltrasoundTransform.PostMultiply() # worldToImage * needleTipToWorld
    needleTipToUltrasoundTransform.Concatenate( self.needleTipToWorldMatrix )
    needleTipToUltrasoundTransform.Concatenate( worldToUltrasoundMatrix )
    
    needleTipToUltrasoundMatrix = vtk.vtkMatrix4x4()
    needleTipToUltrasoundTransform.GetMatrix( needleTipToUltrasoundMatrix )

    
    # The ultrasound image plane is the XY plane, the normal of this plane is the Z-vector
    # Distance between the needletip and XY plane is the value of the Z-coordinate of the needletip
    distanceInPixels = needleTipToUltrasoundMatrix.GetElement( 2, 3 ) #Z coordinate of the needletip in image coordinate system

    # Must convert distanceInPixels to distanceInMm using the scale factor found in the NeedleTipToImage matrix
    # Note: This only works for similarity matrix (i.e. uniform scale factor)
    scaleFactor = math.pow( needleTipToUltrasoundMatrix.Determinant(), 1.0 / 3.0 )
    self.currDistanceMm = math.fabs(distanceInPixels / scaleFactor)

    
    # Angle between a line and a plane is equal to the complementary acute angle that forms
    # between the direction vector of the line and the normal vector of the plane

    # Find the needle direction vector in the image coordinate system
    needleDirection_NeedleTip = [ 0, 0, 1, 0 ] # Assume the needle orientation protocol specifies the needle points in the z direction (+/- is irrelevant)
    needleDirection_Ultrasound = [ 0, 0, 0, 0 ]
    needleTipToUltrasoundMatrix.MultiplyPoint( needleDirection_NeedleTip, needleDirection_Ultrasound )
    needleDirection_Ultrasound = needleDirection_Ultrasound[ 0:3 ] # Truncate to make a 3D vector
    vtk.vtkMath.Normalize( needleDirection_Ultrasound )

    # The unit normal vector of the plane shall be used in the calculation of the angle between the two vectors (theta)
    usPlaneNormal_Ultrasound = [ 0, 0, 1 ]
    needlePlaneAngleDeg = vtk.vtkMath.DegreesFromRadians( vtk.vtkMath.AngleBetweenVectors( needleDirection_Ultrasound, usPlaneNormal_Ultrasound ) )
    self.currAngleDeg = math.fabs( 90 - needlePlaneAngleDeg ) # The angle between the needletip and ultrasound plane   
    
    
    ## Output the result to the output parameter node
    self.outputParameterNode.SetAttribute( "PerkTutor_NeedlePlaneDistanceMm", str( self.currDistanceMm ) )
    self.outputParameterNode.SetAttribute( "PerkTutor_NeedlePlaneAngleDeg", str( self.currAngleDeg ) )

    

  def GetMetric( self ):
    result = [ self.currDistanceMm, self.currAngleDeg ]
    separator = "\t"    
    return separator.join( map( str, result ) )