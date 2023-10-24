from PythonMetricsCalculator import PerkEvaluatorMetric

class Timestamps( PerkEvaluatorMetric ):

  # Static methods
  @staticmethod
  def GetMetricName():
    return "Timestamps"
  
  @staticmethod  
  def GetMetricUnit():
    return "count"
  
  
  # Instance methods  
  def __init__( self ):
    PerkEvaluatorMetric.__init__( self )
  
    self.numTimestamps = 0
    
  def AddTimestamp( self, time, matrix, point, role ):
    self.numTimestamps += 1
    
  def GetMetric( self ):
    return self.numTimestamps