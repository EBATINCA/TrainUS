import math
import vtk
from PythonMetricsCalculator import PerkEvaluatorMetric

class TraceTrajectory( PerkEvaluatorMetric ):

  # Static methods
  @staticmethod
  def GetMetricName():
    return "Trace Trajectory"
  
  @staticmethod  
  def GetMetricUnit():
    return ""
  
  @staticmethod
  def GetAnatomyRoles():
    return { "OutputModel": "vtkMRMLModelNode" }
    
    
  # Instance methods
  def __init__( self ):
    PerkEvaluatorMetric.__init__( self )
    
    self.curvePoints = vtk.vtkPoints()
    self.curveLines = vtk.vtkCellArray()
    self.curvePolyData = vtk.vtkPolyData()
    self.counter = 0
    
    self.curvePolyData.SetPoints( self.curvePoints )
    self.curvePolyData.SetLines( self.curveLines )
    
  def SetAnatomy( self, role, node ):   
    if ( role == "OutputModel" ):
      node.SetAndObservePolyData( self.curvePolyData )
      if ( node.GetModelDisplayNode() is None ):
        node.CreateDefaultDisplayNodes()
      modelDisplayNode = node.GetModelDisplayNode()
      return True
      
    return False
       
  def AddTimestamp( self, time, matrix, point, role ):  
    # Some initialization for the first point
    if ( self.curveLines.GetNumberOfCells() == 0 ):
      self.curvePoints.InsertNextPoint( point[ 0 ], point[ 1 ], point[ 2 ] )
      self.curveLines.InsertNextCell( 1 )
      self.curveLines.InsertCellPoint( 0 )
  
    self.curvePoints.InsertPoint( self.counter + 1, point[ 0 ], point[ 1 ], point[ 2 ] )
    
    self.curveLines.InsertNextCell( 2 ) # Because there are two points in the cell
    self.curveLines.InsertCellPoint( self.counter )
    self.curveLines.InsertCellPoint( self.counter + 1 )
    self.counter += 1