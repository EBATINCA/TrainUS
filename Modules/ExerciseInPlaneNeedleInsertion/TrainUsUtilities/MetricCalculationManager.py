from __main__ import vtk, slicer
import logging
import numpy as np

#------------------------------------------------------------------------------
#
# MetricCalculationManager
#
#------------------------------------------------------------------------------
class MetricCalculationManager:

  #------------------------------------------------------------------------------
  def __init__( self ):

    # Tool reference points
    self.NEEDLE_TIP = [0.0, 0.0, 0.0]
    self.NEEDLE_HANDLE = [0.0, 0.0, -50.0]
    self.USPROBE_TIP = [0.0, 0.0, 0.0]
    self.USPROBE_HANDLE = [0.0, 50.0, 0.0]
    self.USPLANE_ORIGIN = [0.0, 0.0, 0.0]
    self.USPLANE_NORMAL = [0.0, 0.0, 1.0]

    # Current tool positions
    self.needleTip_currentPosition = None
    self.needleHandle_currentPosition = None
    self.usProbeTip_currentPosition = None
    self.usProbeHandle_currentPosition = None
    self.usPlaneCentroid_currentPosition = None
    self.usPlaneNormal_currentPosition = None

  #------------------------------------------------------------------------------
  def getCurrentToolPositions(self, needleTipToNeedleTransform, probeModelToProbeTransform, usImageToProbeTransform):
    # Get needle position
    self.needleTip_currentPosition = self.getTransformedPoint(self.NEEDLE_TIP, needleTipToNeedleTransform)
    self.needleHandle_currentPosition = self.getTransformedPoint(self.NEEDLE_HANDLE, needleTipToNeedleTransform)

    # Get US probe position
    self.usProbeTip_currentPosition = self.getTransformedPoint(self.USPROBE_TIP, probeModelToProbeTransform)
    self.usProbeHandle_currentPosition = self.getTransformedPoint(self.USPROBE_HANDLE, probeModelToProbeTransform)

    # Get US image plane orientation
    usPlanePointA = self.getTransformedPoint(self.USPLANE_ORIGIN, usImageToProbeTransform)
    usPlanePointB = self.getTransformedPoint(self.USPLANE_NORMAL, usImageToProbeTransform)
    self.usPlaneCentroid_currentPosition = usPlanePointA
    self.usPlaneNormal_currentPosition = (usPlanePointB - usPlanePointA) / np.linalg.norm(usPlanePointB - usPlanePointA)

  #------------------------------------------------------------------------------
  def computeNeedleTipToUsPlaneDistanceMm(self):
    """
    Compute the distance in mm from the needle tip to the ultrasound image plane.
    :return float: output distance value in mm
    """
    # Compute distance from point to plane
    distance = self.computeDistancePointToPlane(self.needleTip_currentPosition, self.usPlaneCentroid_currentPosition, self.usPlaneNormal_currentPosition)
    
    return distance

  #------------------------------------------------------------------------------
  def computeNeedleToUsPlaneAngleDeg(self):
    """
    Compute the angle in degrees between the needle and the US plane.
    :return float: output angle value in degrees
    """
    # Project needle points into US plane
    needleTip_proj = self.projectPointToPlane(self.needleTip_currentPosition, self.usPlaneCentroid_currentPosition, self.usPlaneNormal_currentPosition)
    needleHandle_proj = self.projectPointToPlane(self.needleHandle_currentPosition, self.usPlaneCentroid_currentPosition, self.usPlaneNormal_currentPosition)

    # Define needle vector
    needleVector = self.needleTip_currentPosition - self.needleHandle_currentPosition

    # Define needle projection vector
    needleProjectionVector = needleTip_proj - needleHandle_proj

    # Compute angular deviation
    angle = self.computeAngularDeviation(needleVector, needleProjectionVector)

    return angle

  #------------------------------------------------------------------------------
  def computeNeedleTipToTargetDistanceMm(self, targetPoint):
    """
    Compute the distance in mm from the needle tip to a target 3D point.
    :param targetPoint: target point position (numpy array)
    :return float: output distance value in mm
    """
    # Compute distance from point to point
    distance = self.computeDistancePointToPoint(self.needleTip_currentPosition, targetPoint)
    
    return distance  

  #------------------------------------------------------------------------------
  def computeNeedleToTargetLineInPlaneAngleDeg(self, targetLineStart, targetLineEnd):
    """
    Compute the angle in degrees between the needle and the target line.
    :param targetLineStart: target line start position (numpy array)
    :param targetLineEnd: target line end position (numpy array)
    :return float: output angle value in degrees
    """
    # Project needle points into US plane
    needleTip_proj = self.projectPointToPlane(self.needleTip_currentPosition, self.usPlaneCentroid_currentPosition, self.usPlaneNormal_currentPosition)
    needleHandle_proj = self.projectPointToPlane(self.needleHandle_currentPosition, self.usPlaneCentroid_currentPosition, self.usPlaneNormal_currentPosition)

    # Project target line points into US plane (NOT NEEDED, SINCE LINE IS SUPPOSED TO BE WITHIN PLANE)
    targetLineStart_proj = self.projectPointToPlane(targetLineStart, self.usPlaneCentroid_currentPosition, self.usPlaneNormal_currentPosition)
    targetLineEnd_proj = self.projectPointToPlane(targetLineEnd, self.usPlaneCentroid_currentPosition, self.usPlaneNormal_currentPosition)

    # Define needle projection vector
    needleProjectionVector = needleTip_proj - needleHandle_proj

    # Define target projection vector
    targetProjectionVector = targetLineEnd_proj - targetLineStart_proj    

    # Compute angular deviation
    angle = self.computeAngularDeviation(needleProjectionVector, targetProjectionVector)

    return angle

  #------------------------------------------------------------------------------
  def computeDistancePointToPoint(self, fromPoint, toPoint):

    # Compute distance
    distance = np.linalg.norm(np.array(toPoint) - np.array(fromPoint))

    return distance

  #------------------------------------------------------------------------------
  def computeDistancePointToPlane(self, point, planeCentroid, planeNormal):

    # Project point to plane
    projectedPoint = self.projectPointToPlane(point, planeCentroid, planeNormal)
    
    # Compute distance
    distance = np.linalg.norm(np.array(projectedPoint) - np.array(point))

    return distance

  #------------------------------------------------------------------------------
  def projectPointToPlane(self, point, planeCentroid, planeNormal):

    # Project point to plane
    projectedPoint = np.subtract(np.array(point), np.dot(np.subtract(np.array(point), np.array(planeCentroid)), np.array(planeNormal)) * np.array(planeNormal))
    
    return projectedPoint

  # ------------------------------------------------------------------------------
  def computeAngularDeviation(self, vec1, vec2):
    """
    Compute angle between two vectors.

    :param vec1: Vector 1 numpy array
    :param vec2: Vector 2 numpy array

    :return float: Angle between vector 1 and vector 2 in degrees.
    """
    try:
      # Cosine value
      cos_value = np.dot(vec1,vec2)/(np.linalg.norm(vec1)*np.linalg.norm(vec2))
      # Cosine value can only be between [-1, 1].
      if cos_value > 1.0:
        cos_value = 1.0
      elif cos_value < -1.0:
        cos_value = -1.0
      # Compute angle in degrees
      angle = np.rad2deg (np.arccos(cos_value))
    except:
      angle = -1.0
    return angle

  #------------------------------------------------------------------------------
  def getTransformedPoint(self, point, transformNode):

    # Convert to homogenous coordinates
    point_hom = np.hstack((np.array(point), 1.0))

    # Get transform to world
    if transformNode:
      transformToWorld_array = self.getToolToWorldTransform(transformNode)
    else:
      transformToWorld_array = np.eye(4) # identity

    # Get world to ultrasound transform
    #worldToUltrasound_array = self.getWorldToUltrasoundTransform()
    
    # Get transformed point
    point_transformed_hom = np.dot(transformToWorld_array, point_hom)
    #point_transformed_hom = np.dot(worldToUltrasound_array, np.dot(transformToWorld_array, point_hom))

    # Output points
    point_transformed = np.array([point_transformed_hom[0], point_transformed_hom[1], point_transformed_hom[2]])

    return point_transformed

  #------------------------------------------------------------------------------
  def getToolToParentTransform(self, node):
    # Get matrix
    transform_matrix = vtk.vtkMatrix4x4() # vtk matrix
    node.GetMatrixTransformToParent(transform_matrix) # get vtk matrix
    return self.convertVtkMatrixToNumpyArray(transform_matrix)

  #------------------------------------------------------------------------------
  def getToolToWorldTransform(self, node):
    # Get matrix
    transform_matrix = vtk.vtkMatrix4x4() # vtk matrix
    node.GetMatrixTransformToWorld(transform_matrix) # get vtk matrix
    return self.convertVtkMatrixToNumpyArray(transform_matrix)

  #------------------------------------------------------------------------------
  def getWorldToUltrasoundTransform(self):

    if not self.ImageToProbe:
      logging.error('ImageToProbe transform does not exist. WorldToUltrasoundTransform cannot be computed.')

    # Get transform from image to world
    ultrasoundToWorldMatrix = vtk.vtkMatrix4x4()
    self.ImageToProbe.GetMatrixTransformToWorld(ultrasoundToWorldMatrix)

    # Get inverse transform
    worldToUltrasoundMatrix = vtk.vtkMatrix4x4()
    worldToUltrasoundMatrix.DeepCopy( ultrasoundToWorldMatrix )
    worldToUltrasoundMatrix.Invert()

    # Get numpy array
    worldToUltrasoundArray = self.convertVtkMatrixToNumpyArray(worldToUltrasoundMatrix)
    return worldToUltrasoundArray

  #------------------------------------------------------------------------------
  def convertVtkMatrixToNumpyArray(self, vtkMatrix):
    # Build array
    R00 = vtkMatrix.GetElement(0, 0) 
    R01 = vtkMatrix.GetElement(0, 1) 
    R02 = vtkMatrix.GetElement(0, 2)
    Tx = vtkMatrix.GetElement(0, 3)
    R10 = vtkMatrix.GetElement(1, 0)
    R11 = vtkMatrix.GetElement(1, 1)
    R12 = vtkMatrix.GetElement(1, 2)
    Ty = vtkMatrix.GetElement(1, 3)
    R20 = vtkMatrix.GetElement(2, 0)
    R21 = vtkMatrix.GetElement(2, 1)
    R22 = vtkMatrix.GetElement(2, 2)
    Tz = vtkMatrix.GetElement(2, 3)
    H0 = vtkMatrix.GetElement(3, 0)
    H1 = vtkMatrix.GetElement(3, 1)
    H2 = vtkMatrix.GetElement(3, 2)
    H3 = vtkMatrix.GetElement(3, 3)
    return np.array([[R00, R01, R02, Tx],[R10, R11, R12, Ty], [R20, R21, R22, Tz], [H0, H1, H2, H3]])
