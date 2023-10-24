import math
from PythonMetricsCalculator import PerkEvaluatorMetric

# Use Welford's algorithm - this works in real-time and is robust
class RMSMetric( PerkEvaluatorMetric ):

  # Static methods
  @staticmethod
  def GetMetricName():
    return "RMS"
  
  @staticmethod  
  def GetMetricUnit():
    return "mm"
    
    
  # Instance methods  
  def __init__( self ):
    PerkEvaluatorMetric.__init__( self )
  
    self.Mx = None
    self.My = None
    self.Mz = None
    
    self.Sx = None
    self.Sy = None
    self.Sz = None

    self.count = 0   
    
  def AddTimestamp( self, time, matrix, point, role ):    
    if ( self.count == 0 ):
      self.count += 1
      self.Mx = point[ 0 ]
      self.My = point[ 1 ]
      self.Mz = point[ 2 ]
      self.Sx = 0
      self.Sy = 0
      self.Sz = 0
      return
      
    self.count += 1
    
    # Each dimension for variance
    self.Sx = self.Sx + ( self.count - 1 ) * ( point[ 0 ] - self.Mx ) * ( point[ 0 ] - self.Mx ) / self.count
    self.Sy = self.Sy + ( self.count - 1 ) * ( point[ 1 ] - self.My ) * ( point[ 1 ] - self.My ) / self.count
    self.Sz = self.Sz + ( self.count - 1 ) * ( point[ 2 ] - self.Mz ) * ( point[ 2 ] - self.Mz ) / self.count
    
    # Each dimension for mean
    self.Mx = self.Mx + ( point[ 0 ] - self.Mx ) / self.count
    self.My = self.My + ( point[ 1 ] - self.My ) / self.count
    self.Mz = self.Mz + ( point[ 2 ] - self.Mz ) / self.count
    
    
  def GetMetric( self ):    
    # Each of self.Sx, self.Sy, and self.Sz is the sum of squares difference from the mean
    return math.sqrt( ( self.Sx + self.Sy + self.Sz ) / self.count )
