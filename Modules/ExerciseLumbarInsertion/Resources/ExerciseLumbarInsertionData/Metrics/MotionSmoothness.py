import math
import vtk
from PythonMetricsCalculator import PerkEvaluatorMetric

class MotionSmoothness( PerkEvaluatorMetric ):

  # Static methods
  @staticmethod
  def GetMetricName():
    return "Motion Smoothness"
  
  @staticmethod  
  def GetMetricUnit():
    return "mm/s^3"
    
    
  # Instance methods  
  def __init__( self ):
    PerkEvaluatorMetric.__init__( self )
    
    self.squaredJerk = 0
    
    self.pointPrev1 = None
    self.pointPrev2 = None
    self.pointPrev3 = None
    
    self.timePrev1 = None
    self.timePrev2 = None
    self.timePrev3 = None
        
  def AddTimestamp( self, time, matrix, point, role ):  
    if ( time == self.timePrev1 or time == self.timePrev2 or time == self.timePrev3 ):
      return

    if ( self.pointPrev3 == None or self.timePrev3 == None ):
      if ( self.pointPrev2 != None and self.timePrev2 != None ):
        self.pointPrev3 = self.pointPrev2[:]
        self.timePrev3 = self.timePrev2
      if ( self.pointPrev1 != None ):
        self.pointPrev2 = self.pointPrev1[:]
        self.timePrev2 = self.timePrev1
      if ( point != None ):
        self.pointPrev1 = point[:]
        self.timePrev1 = time
        
      return
    
    # Note that we are using backward difference formulas here
    # We might use central difference formulas for better accuracy, but it couldn't be extensible to real-time    
    timeDiff01 = time - self.timePrev1
    timeDiff12 = self.timePrev1 - self.timePrev2
    timeDiff23 = self.timePrev2 - self.timePrev3
    
    velocity0 = [ 0, 0, 0 ]
    vtk.vtkMath().Subtract( point[0:3], self.pointPrev1[0:3], velocity0 )
    velocity0 = [ velocity0[ 0 ] / timeDiff01, velocity0[ 1 ] / timeDiff01, velocity0[ 2 ] / timeDiff01 ]

    velocity1 = [ 0, 0, 0 ]
    vtk.vtkMath().Subtract( self.pointPrev1[0:3], self.pointPrev2[0:3], velocity1 )
    velocity1 = [ velocity1[ 0 ] / timeDiff12, velocity1[ 1 ] / timeDiff12, velocity1[ 2 ] / timeDiff12 ]

    velocity2 = [ 0, 0, 0 ]
    vtk.vtkMath().Subtract( self.pointPrev2[0:3], self.pointPrev3[0:3], velocity2 )
    velocity2 = [ velocity2[ 0 ] / timeDiff23, velocity2[ 1 ] / timeDiff23, velocity2[ 2 ] / timeDiff23 ]

    acceleration0 = [ 0, 0, 0 ]
    vtk.vtkMath().Subtract( velocity0, velocity1, acceleration0 )
    acceleration0 = [ acceleration0[ 0 ] / timeDiff01, acceleration0[ 1 ] / timeDiff01, acceleration0[ 2 ] / timeDiff01 ]

    acceleration1 = [ 0, 0, 0 ]
    vtk.vtkMath().Subtract( velocity1, velocity2, acceleration1 )
    acceleration1 = [ acceleration1[ 0 ] / timeDiff12, acceleration1[ 1 ] / timeDiff12, acceleration1[ 2 ] / timeDiff12 ]

    jerk = [ 0, 0, 0 ]
    vtk.vtkMath().Subtract( acceleration0, acceleration1, jerk )
    jerk = [ jerk[ 0 ] / timeDiff01, jerk[ 1 ] / timeDiff01, jerk[ 2 ] / timeDiff01 ]

    jerkMagnitude = math.pow( jerk[ 0 ], 2 ) + math.pow( jerk[ 1 ], 2 ) + math.pow( jerk[ 2 ], 2 )
    self.squaredJerk += jerkMagnitude * timeDiff01

    self.pointPrev3 = self.pointPrev2[:] # Require element copy 
    self.timePrev3 = self.timePrev2
    self.pointPrev2 = self.pointPrev1[:] # Require element copy 
    self.timePrev2 = self.timePrev1
    self.pointPrev1 = point[:] # Require element copy 
    self.timePrev1 = time

    
  def GetMetric( self ):
    return math.sqrt( self.squaredJerk )