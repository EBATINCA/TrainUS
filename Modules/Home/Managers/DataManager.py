from __main__ import vtk, qt, ctk, slicer
import logging
import os
import numpy as np
import json
import shutil

#------------------------------------------------------------------------------
#
# DataManager
#
#------------------------------------------------------------------------------
class DataManager():

  def __init__(self):
  	# Root directory
    self.rootDirectory = ''

  #------------------------------------------------------------------------------
  def setRootDirectory(self, dataPath):
    self.rootDirectory = dataPath

  #------------------------------------------------------------------------------
  def getRootDirectory(self):
    return self.rootDirectory

  #------------------------------------------------------------------------------
  def readRootDirectory(self):
    """
    Reads all the files in the root directory to get the list of participants in the database.

    :return list: list of dictionaries containing the information of all participants in the database
    """
    logging.debug('DataManager.readRootDirectory')

    # Get root directory
    dataPath = self.rootDirectory

    # Get participants
    participantID_list = self.getListOfFoldersInDirectory(dataPath)

    # Get participant info
    participantInfo_list = list() # list of dictionaries
    for participantID in participantID_list:
      # Participant info file
      participantInfoFilePath = self.getParticipantInfoFilePath(participantID)

      # Get participant info
      participantInfo = self.readParticipantInfoFile(participantInfoFilePath)
      participantInfo_list.append(participantInfo)

    # Display
    print('\n>>>>>Home.readRootDirectory<<<<<<<<<<<<')
    print('\nDirectory: ', dataPath)
    print('\nParticipants in directory: ', participantID_list)
    print('\nInfo JSON: ', participantInfo_list)

    return participantInfo_list

  #------------------------------------------------------------------------------
  def filterParticipantInfoListFromSearchText(self, participantInfo_list, searchText):
    """
    Filters participant information list of dictionaries to keep only those participant matching the search criteria.

    :param participantInfo_list: list of dictionaries containing the information of all participants in the database (list)
    :param searchText: input text in search box (string)

    :return list: list of dictionaries containing the information of all participants matching search criteria
    """
    logging.debug('DataManager.filterParticipantInfoListFromSearchText')

    # Get number of participants in input list
    numParticipants = len(participantInfo_list)

    # Convert input search text to lower case
    searchText = searchText.lower()

    # Create filtered list
    participantInfoFiltered_list = list()
    if numParticipants >= 0:
      for participantPos in range(numParticipants):
        participantName = participantInfo_list[participantPos]['name'] # Get name
        participantSurname = participantInfo_list[participantPos]['surname'] # Get surname
        participantString = participantName + ' ' + participantSurname # Create single string with participant name and surname
        participantString = participantString.lower() # convert to lower case
        if searchText in participantString: # keep participants meeting search criteria
          participantInfoFiltered_list.append(participantInfo_list[participantPos])
    return participantInfoFiltered_list  

  #------------------------------------------------------------------------------
  def readParticipantDirectory(self, participantID):
    """
    Reads participant directory to get the list of recordings in the database.

    :return tuple: participant IDs (list), participant names (list), participant surnames (list), and participant
                  number of recordings (list)
    """
    logging.debug('DataManager.readParticipantDirectory')

    # Get root directory
    dataPath = self.rootDirectory

    # Participant directory
    participantDirectory = os.path.join(dataPath, participantID)
    print('DataManager.readParticipantDirectory: participant directory: ', participantDirectory)

    # Get recordings
    recordingID_list = self.getListOfFoldersInDirectory(participantDirectory)
    print('DataManager.readParticipantDirectory: participant directory: ', recordingID_list)

    # Get participant info
    recordingInfo_list = list() # list of dictionaries
    for recordingID in recordingID_list:
      # Get recording info
      recordingInfo = self.getRecordingInfoFromID(participantID, recordingID)
      if recordingInfo is not None:
        recordingInfo_list.append(recordingInfo)

    # Display
    print('\n>>>>>Home.readParticipantDirectory<<<<<<<<<<<<')
    print('\nDirectory: ', participantDirectory)
    print('\nRecordings in directory: ', recordingID_list)
    print('\nInfo JSON: ', recordingInfo_list)  

    return recordingInfo_list  

  #------------------------------------------------------------------------------
  def getListOfFoldersInDirectory(self, directory):
    """
    Gets list of folders contained in input directory.

    :param directory: input directory (string)

    :return list of folder names (list)
    """
    dirfiles = os.listdir(directory)
    fullpaths = map(lambda name: os.path.join(directory, name), dirfiles)
    folderList = []
    for fileID, filePath in enumerate(fullpaths):
      if os.path.isdir(filePath): 
        folderList.append(dirfiles[fileID])
    return list(folderList)

  #------------------------------------------------------------------------------
  def readParticipantInfoFile(self, filePath):
    """
    Reads participant's information from .json file.

    :param filePath: path to JSON file (string)

    :return participant info (dict)
    """
    try:
      with open(filePath, 'r') as inputFile:
        participantInfo =  json.loads(inputFile.read())
    except:
      logging.error('Cannot read participant information from JSON file at ' + filePath)
      participantInfo = None
    return participantInfo
  
  #------------------------------------------------------------------------------
  def readRecordingInfoFile(self, filePath):
    """
    Reads recording's information from .json file.

    :param filePath: path to JSON file (string)

    :return recording info (dict)
    """
    try:
      with open(filePath, 'r') as inputFile:
        recordingInfo =  json.loads(inputFile.read())
    except:
      logging.error('Cannot read recording information from JSON file at ' + filePath)
      recordingInfo = None
    return recordingInfo
  
  #------------------------------------------------------------------------------
  def writeParticipantInfoFile(self, filePath, participantInfo):
    """
    Writes participant's information (name and surname) to .txt file.

    :param filePath: path to file (string)
    :param participantInfo: participant information (dict)
    """
    with open(filePath, "w") as outputFile:
      json.dump(participantInfo, outputFile, indent = 4)

  #------------------------------------------------------------------------------
  def getParticipantInfoFromID(self, participantID):
    """
    Get participant's information from participant ID.

    :param participantID: participant ID (string)

    :return participant info (dict)
    """
    # Abort if participant ID is not invalid
    if participantID == '':
      return

    # Participant info file
    participantInfoFilePath = self.getParticipantInfoFilePath(participantID)
    
    # Read participant info
    participantInfo = self.readParticipantInfoFile(participantInfoFilePath)

    return participantInfo

  #------------------------------------------------------------------------------
  def getRecordingInfoFromID(self, participantID, recordingID):
    """
    Get recording's information from participant ID and recording ID.

    :param participantID: participant ID (string)
    :param recordingID: recording ID (string)

    :return recording info (dict)
    """
    # Abort if recording ID is not invalid
    if (participantID == '') or (recordingID == ''):
      return

    # Recording info file
    recordingInfoFilePath = self.getRecordingInfoFilePath(participantID, recordingID)
    
    # Read recording info
    recordingInfo = self.readRecordingInfoFile(recordingInfoFilePath)

    return recordingInfo

  #------------------------------------------------------------------------------
  def getParticipantInfoFilePath(self, participantID):
    """
    Get path to participant's information JSON file.

    :param participantID: participant ID (string)

    :return participant info (dict)
    """
    # Set root directory
    dataPath = self.rootDirectory

    # Participant directory
    participantDirectory = os.path.join(dataPath, participantID)

    # Participant info file
    participantInfoFilePath = os.path.join(participantDirectory, 'Participant_Info.json')

    return participantInfoFilePath

  #------------------------------------------------------------------------------
  def getRecordingInfoFilePath(self, participantID, recordingID):
    """
    Get path to recording's information JSON file.

    :param participantID: participant ID (string)
    :param recordingID: recording ID (string)

    :return recording info (dict)
    """
    # Set root directory
    dataPath = self.rootDirectory

    # Participant directory
    participantDirectory = os.path.join(dataPath, participantID)

    # Recording directory
    recordingDirectory = os.path.join(participantDirectory, recordingID)

    # Participant info file
    recordingInfoFilePath = os.path.join(recordingDirectory, 'Recording_Info.json')

    return recordingInfoFilePath

  #------------------------------------------------------------------------------
  def getParticipantInfoFromSelection(self):
    """
    Get participant's information from selection stored in parameter node.

    :return participant info (dict)
    """
    # Get selected participant
    selectedParticipantID = self.getSelectedParticipantID()

    # Get participant info from ID
    selectedParticipantInfo = self.getParticipantInfoFromID(selectedParticipantID)

    return selectedParticipantInfo

  #------------------------------------------------------------------------------
  def getRecordingInfoFromSelection(self):
    """
    Get recording's information from selection stored in parameter node.

    :return recording info (dict)
    """
    # Get selected participant and recording
    selectedParticipantID = self.getSelectedParticipantID()
    selectedRecordingID = self.getSelectedRecordingID()

    # Get participant info from ID
    selectedRecordingInfo = self.getRecordingInfoFromID(selectedParticipantID, selectedRecordingID)

    return selectedRecordingInfo

  #------------------------------------------------------------------------------
  def deleteParticipant(self, participantID):
    """
    Delete participant from root directory.

    :param participantID: participant ID (string)
    """
    logging.debug('DataManager.deleteParticipant')

    # Set root directory
    dataPath = self.rootDirectory

    # Participant directory
    participantDirectory = os.path.join(dataPath, participantID)

    # Delete folder
    shutil.rmtree(participantDirectory, ignore_errors=True)

  #------------------------------------------------------------------------------
  def deleteSelectedParticipant(self):
    """
    Delete selected participant from root directory.
    """
    # Get selected participant
    selectedParticipantID = self.getSelectedParticipantID()

    # Delete participant
    self.deleteParticipant(selectedParticipantID)
    
    # Unselect participant
    self.setSelectedParticipantID('')

  #------------------------------------------------------------------------------
  def deleteRecording(self, participantID, recordingID):
    """
    Delete recording from root directory.

    :param participantID: participant ID (string)
    :param recordingID: recording ID (string)
    """
    logging.debug('DataManager.deleteRecording')

    # Set root directory
    dataPath = self.rootDirectory

    # Recording directory
    participantDirectory = os.path.join(dataPath, participantID)
    recordingDirectory = os.path.join(participantDirectory, recordingID)

    # Delete folder
    shutil.rmtree(recordingDirectory, ignore_errors=True)

  #------------------------------------------------------------------------------
  def deleteSelectedRecording(self):
    """
    Delete selected recording from root directory.
    """
    # Get selected participant and recording
    selectedParticipantID = self.getSelectedParticipantID()
    selectedRecordingID = self.getSelectedRecordingID()

    # Delete recording
    self.deleteRecording(selectedParticipantID, selectedRecordingID)
    
    # Unselect recording
    self.setSelectedRecordingID('')

  #------------------------------------------------------------------------------
  def createNewParticipant(self, participantName, participantSurname, participantBirthDate, participantEmail):
    """
    Adds new participant to database by generating a unique ID, creating a new folder, 
    and creating a new .txt file containing participant information.

    :param participantName: participant name (string)
    :param participantSurname: participant surname (string)
    :param participantBirthDate: participant birth date (string)
    :param participantEmail: participant email (string)

    :return new participant info (dict)
    """
    logging.debug('DataManager.createNewParticipant')

    # Get data from directory
    participantInfo_list = self.readRootDirectory()

    # Get existing participant IDs
    numParticipants = len(participantInfo_list)
    participantID_list = []
    for participant in range(numParticipants):
      participantID_list.append(participantInfo_list[participant]['id'])

    # Generate new participant ID (TODO: improve to ensure uniqueness)
    participantID_array = np.array(participantID_list).astype(int)
    try:
      maxParticipantID = np.max(participantID_array)
    except:
      maxParticipantID = 0
    newParticipantID = str("{:05d}".format(maxParticipantID + 1)) # leading zeros, 5 digits

    # Set root directory
    dataPath = self.rootDirectory

    # Create participant folder
    participantDirectory = os.path.join(dataPath, str(newParticipantID))
    try:
      os.makedirs(participantDirectory)    
      logging.debug('Participant directory was created')
    except FileExistsError:
      logging.debug('Participant directory already exists')

    # Create participant info dictionary
    participantInfo = {}
    participantInfo['id'] = newParticipantID
    participantInfo['name'] = participantName
    participantInfo['surname'] = participantSurname
    participantInfo['birthdate'] = participantBirthDate
    participantInfo['email'] = participantEmail

    # Create info file
    participantInfoFilePath = self.getParticipantInfoFilePath(newParticipantID)
    self.writeParticipantInfoFile(participantInfoFilePath, participantInfo)

    # Update participant selection
    self.setSelectedParticipantID(participantInfo['id'])

    return participantInfo

  #------------------------------------------------------------------------------
  def editParticipantInfo(self, participantName, participantSurname, participantBirthDate, participantEmail):
    """
    Edit name and surname of the selected participant in the JSON info file.
    :param participantName: new name for partipant (string)
    :param participantSurname: new surname for participant (string)
    """    
    # Get selected participant info
    selectedParticipantInfo = self.getParticipantInfoFromSelection() 

    # Get JSON info file path
    selectedParticipantID = selectedParticipantInfo['id']
    participantInfoFilePath = self.getParticipantInfoFilePath(selectedParticipantID)

    # Edit participant info
    selectedParticipantInfo['name'] = participantName
    selectedParticipantInfo['surname'] = participantSurname
    selectedParticipantInfo['birthdate'] = participantBirthDate
    selectedParticipantInfo['email'] = participantEmail

    # Write new file
    self.writeParticipantInfoFile(participantInfoFilePath, selectedParticipantInfo)

    # Update participant selection
    self.setSelectedParticipantID(selectedParticipantID)

  #------------------------------------------------------------------------------
  def isParticipantSelected(self):
    """
    Check if a participant is selected.
    :return bool: True if valid participant is selected, False otherwise
    """    
    # Get selected participant
    selectedParticipantID = self.getSelectedParticipantID()

    # Check valid selection
    if (selectedParticipantID == '') :
      participantSelected = False
    else:
      participantSelected = True
    return participantSelected

  #------------------------------------------------------------------------------
  def getSelectedParticipantID(self):
    """
    Get selected participant ID.
    """
    # Parameter node
    parameterNode = slicer.trainUsWidget.getParameterNode()
    if not parameterNode:
      logging.error('Failed to get parameter node')
      return

    # Get selected participant
    selectedParticipantID = parameterNode.GetParameter(slicer.trainUsWidget.logic.selectedParticipantIDParameterName)
    return selectedParticipantID

  #------------------------------------------------------------------------------
  def setSelectedParticipantID(self, participantID):
    """
    Set selected participant ID.
    """
    # Parameter node
    parameterNode = slicer.trainUsWidget.getParameterNode()
    if not parameterNode:
      logging.error('Failed to get parameter node')
      return

    # Update parameter node
    parameterNode.SetParameter(slicer.trainUsWidget.logic.selectedParticipantIDParameterName, participantID)

  #------------------------------------------------------------------------------
  def isRecordingSelected(self):
    """
    Check if a recording is selected.
    :return bool: True if valid recording is selected, False otherwise
    """    
    # Get selected recording
    selectedRecordingID = self.getSelectedRecordingID()

    # Check valid selection
    if (selectedRecordingID == '') :
      recordingSelected = False
    else:
      recordingSelected = True
    return recordingSelected

  #------------------------------------------------------------------------------
  def getSelectedRecordingID(self):
    """
    Get selected recording ID.
    """
    # Parameter node
    parameterNode = slicer.trainUsWidget.getParameterNode()
    if not parameterNode:
      logging.error('Failed to get parameter node')
      return

    # Get selected participant
    selectedRecordingID = parameterNode.GetParameter(slicer.trainUsWidget.logic.selectedRecordingIDParameterName)
    return selectedRecordingID

  #------------------------------------------------------------------------------
  def setSelectedRecordingID(self, recordingID):
    """
    Set selected recording ID.
    """
    # Parameter node
    parameterNode = slicer.trainUsWidget.getParameterNode()
    if not parameterNode:
      logging.error('Failed to get parameter node')
      return

    # Update parameter node
    parameterNode.SetParameter(slicer.trainUsWidget.logic.selectedRecordingIDParameterName, recordingID)

  

  
  