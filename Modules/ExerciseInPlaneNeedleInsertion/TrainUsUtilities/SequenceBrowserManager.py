from __main__ import vtk, slicer
import logging

#------------------------------------------------------------------------------
#
# SequenceBrowserManager
#
#------------------------------------------------------------------------------
class SequenceBrowserManager:

  #------------------------------------------------------------------------------
  def __init__( self ):
    # Sequence browser
    self.sequenceBrowserNode = None

    # Recording info
    self.recordingLength = 0.0
    self.recordingInProgress = False

    # Observer
    self.observerID = None

    # Sequences (Sequences extension)
    try:
      self.sequencesLogic = slicer.modules.sequences.logic()
    except:
      logging.error('ERROR: "Sequences" module was not found.')

  #------------------------------------------------------------------------------
  def getSequenceBrowser(self):
    """
    Get sequence browser node
    :return sequence browser node (vtkMRMLSequenceBrowserNode)
    """
    return self.sequenceBrowserNode

  #------------------------------------------------------------------------------
  def getRecordingLength(self):
    """
    Get recording length value
    :return recording length (float)
    """
    return self.recordingLength  

  #------------------------------------------------------------------------------
  def getRecordingInProgress(self):
    """
    Get recording in progress
    :return result (bool)
    """
    return self.recordingInProgress  

  #------------------------------------------------------------------------------
  def isSequenceBrowserEmpty(self):
    """
    Check if sequence browser node is empty or not.
    :return result (bool)
    """
    # Get number of items
    numItems = self.getNumberOfItemsInSequenceBrowser()    
    return (numItems == 0)

  #------------------------------------------------------------------------------
  def getNumberOfItemsInSequenceBrowser(self):
    """
    Get number of items in sequence browser node.
    :return number of items (int)
    """
    # Get number of items
    if self.sequenceBrowserNode:
      numItems = self.sequenceBrowserNode.GetNumberOfItems()
    else:
      numItems = 0
    return numItems

  #------------------------------------------------------------------------------
  def getTimeRangeInSequenceBrowser(self):
    """
    Get time range in sequence browser node
    """
    # Get number of items
    numItems = self.getNumberOfItemsInSequenceBrowser()

    # No range if recording is empty
    if self.isSequenceBrowserEmpty():
      return

    # Get initial and final timestamps
    minValue = float(self.sequenceBrowserNode.GetMasterSequenceNode().GetNthIndexValue(0))
    maxValue = float(self.sequenceBrowserNode.GetMasterSequenceNode().GetNthIndexValue(numItems-1))
    return [minValue, maxValue]

  #------------------------------------------------------------------------------
  def getSelectedItemInSequenceBrowser(self):
    """
    Get selected item number in sequence browser node.
    """
    if self.sequenceBrowserNode:
      selectedItem = self.sequenceBrowserNode.GetSelectedItemNumber()
    else:
      selectedItem = None
    return selectedItem

  #------------------------------------------------------------------------------
  def getSelectedTimestampInSequenceBrowser(self):
    """
    Get selected timestamp in sequence browser node.
    """
    if self.sequenceBrowserNode:
      selectedItem = self.sequenceBrowserNode.GetSelectedItemNumber()
      selectedTimestamp = self.getTimestampFromSequenceBrowserItem(selectedItem)
    else:
      selectedTimestamp = None
    return selectedTimestamp

  #------------------------------------------------------------------------------
  def getSequenceBrowserItemFromTimestamp(self, inputTimestamp):
    """
    Get corresponding item number from give time value.
    """
    if not self.sequenceBrowserNode:
      return

    # Get number of items
    numItems = self.getNumberOfItemsInSequenceBrowser()

    # Get list of timestamps
    timestampsList = list()
    for itemID in range(numItems):
      timestampsList.append(float(self.sequenceBrowserNode.GetMasterSequenceNode().GetNthIndexValue(itemID)))

    # Get closest timestamp
    outputItemID = timestampsList.index(min(timestampsList, key=lambda x:abs(x-inputTimestamp)))
    return outputItemID

  #------------------------------------------------------------------------------
  def getTimestampFromSequenceBrowserItem(self, inputItemID):
    """
    Get corresponding timestamp from item ID.
    """
    try:
      timestamp = self.sequenceBrowserNode.GetMasterSequenceNode().GetNthIndexValue(inputItemID)
    except:
      timestamp = None
    return timestamp

  #------------------------------------------------------------------------------
  def selectFirstItemInSequenceBrowser(self):
    self.sequenceBrowserNode.SelectFirstItem()

  #------------------------------------------------------------------------------
  def SelectNextItemInSequenceBrowser(self):
    self.sequenceBrowserNode.SelectNextItem() 

  #------------------------------------------------------------------------------
  def GetTimestampFromItemID(self, itemID):
    return self.sequenceBrowserNode.GetMasterSequenceNode().GetNthIndexValue(itemID)

  #------------------------------------------------------------------------------
  def createNewSequenceBrowser(self, browserName, synchronizedNodes):
    """
    Create new sequence browser node to manage data recording.    
    :param browserName: sequence browser node name (string)
    :param synchronizedNodes: list of nodes to be synchronized for recording (list)
    :return success (bool)
    """
    try:
      # Create a sequence browser node
      self.sequenceBrowserNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLSequenceBrowserNode', slicer.mrmlScene.GenerateUniqueName(browserName))

      # Start modification
      modifiedFlag = self.sequenceBrowserNode.StartModify()

      # Add synchronized nodes
      for node in synchronizedNodes:
        self.sequencesLogic.AddSynchronizedNode(None, node, self.sequenceBrowserNode)

      # Stop overwritting and saving changes to all nodes
      self.sequenceBrowserNode.SetRecording(None, True)
      self.sequenceBrowserNode.SetOverwriteProxyName(None, False)
      self.sequenceBrowserNode.SetSaveChanges(None, False)

      # Finish modification
      self.sequenceBrowserNode.EndModify(modifiedFlag)
      return True

    except:
      logging.error('Error creating a new sequence browser node...')
      return False

  #------------------------------------------------------------------------------
  def clearSequenceBrowser(self):
    """
    Clear recording data in sequence browser.

    :return success (bool)
    """
    if not self.sequenceBrowserNode:
      return False

    # Remove sequence nodes from scene
    synchronizedSequenceNodes = vtk.vtkCollection()
    self.sequenceBrowserNode.GetSynchronizedSequenceNodes(synchronizedSequenceNodes)
    synchronizedSequenceNodes.AddItem(self.sequenceBrowserNode.GetMasterSequenceNode())
    for sequenceNode in synchronizedSequenceNodes:
      slicer.mrmlScene.RemoveNode(sequenceNode)

    # Remove sequence browser node from scene
    slicer.mrmlScene.RemoveNode(self.sequenceBrowserNode)
    self.sequenceBrowserNode = None 
    self.recordingLength = 0.0

    return True

  #------------------------------------------------------------------------------
  def saveSequenceBrowser(self, filePath):
    """
    Save sequence browser node to file.    
    :param filePath: path to output file (string)
    :return success (bool)
    """
    try:
      slicer.util.saveNode(self.sequenceBrowserNode, filePath)
      success = True
    except:
      logging.error('Error saving sequence browser node to file...')
      success = False
    return success

  #------------------------------------------------------------------------------
  def loadSequenceBrowser(self, filePath):
    """
    Load sequence browser node from file.    
    :param filePath: path to input file (string)
    """
    try:
      self.sequenceBrowserNode = slicer.util.loadNodeFromFile(filePath, 'Tracked Sequence Browser')
      success = True
    except:
      logging.error('Error loading sequence browser node from file...')
      success = False
    return success

  #------------------------------------------------------------------------------
  def trimSequenceBrowserRecording(self, minTimestamp, maxTimestamp):
    """
    Trim sequence browser node. 
    :param minTimestamp: minimum timestamp (float)
    :param maxTimestamp: maximum timestamp (float)
    """
    if not self.sequenceBrowserNode:
      return False

    # Get number of items
    numItems = self.getNumberOfItemsInSequenceBrowser()  

    # Get list of timestamps
    valuesToBeRemoved = list()
    for itemID in range(numItems):
      value = self.sequenceBrowserNode.GetMasterSequenceNode().GetNthIndexValue(itemID)
      if (float(value) < minTimestamp) or (float(value) > maxTimestamp):
        valuesToBeRemoved.append(value)

    # Remove data nodes from sequences
    for value in valuesToBeRemoved:
      self.sequenceBrowserNode.GetMasterSequenceNode().RemoveDataNodeAtValue(value)

    # Select first item
    self.sequenceBrowserNode.SelectFirstItem() # reset
    return True

  #------------------------------------------------------------------------------
  def startSequenceBrowserRecording(self):
    """
    Start recording data using sequence browser node.
    """
    # Create sequence browser if needed
    if not self.sequenceBrowserNode:
      self.createNewSequenceBrowser()

    # Start recording
    try:
      self.sequenceBrowserNode.SetRecordMasterOnly(False)
      self.sequenceBrowserNode.SetRecording(None, True)
      self.sequenceBrowserNode.SetRecordingActive(True)
      success = True
    except:
      logging.error('Error starting sequence browser recording...')
      success = False

    # Update recording in progress flag
    self.recordingInProgress = success
    return success

  #------------------------------------------------------------------------------
  def stopSequenceBrowserRecording(self):
    """
    Stop recording data using sequence browser node.
    """
    # Stop recording
    try:
      self.sequenceBrowserNode.SetRecordingActive(False)
      self.sequenceBrowserNode.SetRecording(None, False)
      self.setPlaybackRealtime()
      success =  True
    except:
      logging.error('Error stopping sequence browser recording...')
      success =  False

    # Update recording in progress flag
    self.recordingInProgress = not success
    return success

  #------------------------------------------------------------------------------
  def setPlaybackRealtime(self):
    """
    Set playback FPS rate to real time.
    """
    try: #- update the playback fps rate
      sequenceNode = self.sequenceBrowserNode.GetMasterSequenceNode()
      numDataNodes = sequenceNode.GetNumberOfDataNodes()
      startTime = float(sequenceNode.GetNthIndexValue(0))
      stopTime = float(sequenceNode.GetNthIndexValue(numDataNodes-1))
      self.recordingLength = stopTime - startTime
      frameRate = numDataNodes / self.recordingLength
      self.sequenceBrowserNode.SetPlaybackRateFps(frameRate)
    except:
      logging.error('Could not set playback realtime fps rate')
