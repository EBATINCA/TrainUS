import math
import vtk
from PythonMetricsCalculator import PerkEvaluatorMetric

class TissuePunctures( PerkEvaluatorMetric ):

  PUNCTURE_THRESHOLD = 5 #mm

  # Static methods
  @staticmethod
  def GetMetricName():
    return "Tissue Punctures"
  
  @staticmethod  
  def GetMetricUnit():
    return "count"
    
  @staticmethod
  def GetTransformRoles():
    return [ "Needle" ]
    
  @staticmethod
  def GetAnatomyRoles():
    return { "Tissue": "vtkMRMLModelNode" }
    
    
  # Instance methods
  def __init__( self ):
    PerkEvaluatorMetric.__init__( self )
  
    self.tissuePunctures = 0
    self.punctureState = False  
    
  def SetAnatomy( self, role, node ):
    if ( role == "Tissue" and node.GetPolyData() != None ):
      self.tissueNode = node
      self.enclosedFilter = vtk.vtkSelectEnclosedPoints()
      self.enclosedFilter.Initialize( self.tissueNode.GetPolyData() )      
      return True
      
    return False

  def AddTimestamp( self, time, matrix, point, role ):      
    # Find the three key points on the needle
    NeedleTip_Shaft = [ 0, 0, 0, 1 ]
    NeedleTip_RAS = [ 0, 0, 0, 1 ]
    NeedleTipForward_Shaft = [ x * 1 for x in self.NeedleOrientation ]
    NeedleTipForward_Shaft.append( 1 )
    NeedleTipForward_RAS = [ 0, 0, 0, 1 ]
    NeedleTipBackward_Shaft = [ x * -1 for x in self.NeedleOrientation ]
    NeedleTipBackward_Shaft.append( 1 )
    NeedleTipBackward_RAS = [ 0, 0, 0, 1 ]
    
    matrix.MultiplyPoint( NeedleTip_Shaft, NeedleTip_RAS )
    matrix.MultiplyPoint( NeedleTipForward_Shaft, NeedleTipForward_RAS )
    matrix.MultiplyPoint( NeedleTipBackward_Shaft, NeedleTipBackward_RAS )
    
    needleTipInside = self.enclosedFilter.IsInsideSurface( NeedleTip_RAS[0], NeedleTip_RAS[1], NeedleTip_RAS[2] )
    needleTipForwardInside = self.enclosedFilter.IsInsideSurface( NeedleTipForward_RAS[0], NeedleTipForward_RAS[1], NeedleTipForward_RAS[2] )
    needleTipBackwardInside = self.enclosedFilter.IsInsideSurface( NeedleTipBackward_RAS[0], NeedleTipBackward_RAS[1], NeedleTipBackward_RAS[2] )
    
    if ( not self.punctureState ):
      if ( needleTipInside and needleTipForwardInside and needleTipBackwardInside ):
        self.tissuePunctures += 1
        self.punctureState = True
        
    if ( self.punctureState ):
      if ( not needleTipInside and not needleTipForwardInside and not needleTipBackwardInside ):
        self.punctureState = False

  def GetMetric( self ):
    return self.tissuePunctures