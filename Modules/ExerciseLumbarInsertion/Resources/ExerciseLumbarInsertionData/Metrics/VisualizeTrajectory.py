import math
import vtk
from PythonMetricsCalculator import PerkEvaluatorMetric

# This should supersede the trace trajectory method
# Use in combination with Slicer Markups To Model to get better visualizations of the trajectory
# Slicer Markups To Model allows visualization methods to be customized
class VisualizeTrajectory( PerkEvaluatorMetric ):

  # Static methods
  @staticmethod
  def GetMetricName():
    return "Visualize Trajectory"
  
  @staticmethod
  def GetAnatomyRoles():
    # Should be the input model for the Markups To Model node
    return { "OutputModel": "vtkMRMLModelNode" }
    
    
  # Instance methods
  def __init__( self ):    
    self.modelPoints = vtk.vtkPoints()
    self.modelPolyData = vtk.vtkPolyData()
    self.modelPolyData.SetPoints( self.modelPoints )
    
  def SetAnatomy( self, role, node ):
    if ( role == "OutputModel" ):
      node.SetAndObservePolyData( self.modelPolyData )
      return True      
    return False
    
  def AddTimestamp( self, time, matrix, point, role ):
    self.modelPoints.InsertNextPoint( point[ 0 ], point[ 1 ], point[ 2 ] )
    
  def GetMetric( self ):
    self.modelPoints.Modified()
    self.modelPolyData.Modified() # Needed for auto-update
    return 0
