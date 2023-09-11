from __main__ import vtk, qt, ctk, slicer
import logging
import os
import numpy as np
import json
import shutil

# TrainUS parameters
import TrainUSLib.TrainUSParameters as Parameters

#------------------------------------------------------------------------------
#
# RecordingManager
#
#------------------------------------------------------------------------------
class RecordingManager():
  """
  Manages data associated with participants and recordings. This class is responsible
  for creating, selecting, editing, and deleting participants and recordings. 

  Data is stored in a root directory where different subfolders are created for parti-
  cipants and recordings, with JSON files to store participant and recording details.
  """
  def __init__(self):
  	# Root directory
    self.rootDirectory = ''

  #------------------------------------------------------------------------------
  #
  # Read root directory
  #
  #------------------------------------------------------------------------------
  
  #------------------------------------------------------------------------------
  def setRootDirectory(self, dataPath):
    """
    Sets the directory of the database where participants' info and recordings' data is stored.
    """
    logging.debug('RecordingManager.setRootDirectory')

    self.rootDirectory = dataPath

  #------------------------------------------------------------------------------
  def getRootDirectory(self):
    """
    Gets the directory of the database where participants' info and recordings' data is stored.

    :return directory to root directory (string)
    """
    logging.debug('RecordingManager.getRootDirectory')

    return self.rootDirectory

  #------------------------------------------------------------------------------
  def readRootDirectory(self):
    """
    Reads all the files in the root directory to get the list of participants in the database.

    :return list of dictionaries containing the information of all participants in the database (list)
    """
    logging.debug('RecordingManager.readRootDirectory')

    # Get list of participant IDs
    participantID_list = self.getListOfFoldersInDirectory(self.rootDirectory)

    # Get individial participant info and store in list of dictionaries
    participantInfo_list = list() # list of dictionaries
    for participantID in participantID_list:
      # Participant info file path
      participantInfoFilePath = self.getParticipantInfoFilePath(participantID)
      # Get participant info
      participantInfo = self.readParticipantInfoFile(participantInfoFilePath)
      participantInfo_list.append(participantInfo)

    # Display
    print('\n>>>>>Home.readRootDirectory<<<<<<<<<<<<')
    print('\nDirectory: ', self.rootDirectory)
    print('\nParticipants in directory: ', participantID_list)
    print('\nInfo JSON: ', participantInfo_list)

    return participantInfo_list

  #------------------------------------------------------------------------------
  def readParticipantDirectory(self, participantID):
    """
    Reads participant directory to get the list of recordings in the database for a given participant.

    :return list of dictionaries containing the information of all recordings in the database (list)
    """
    logging.debug('RecordingManager.readParticipantDirectory')

    # Get participant directory
    participantDirectory = os.path.join(self.rootDirectory, participantID)

    # Get list of recordings for participant
    recordingID_list = self.getListOfFoldersInDirectory(participantDirectory)

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
    logging.debug('RecordingManager.getListOfFoldersInDirectory')

    dirfiles = os.listdir(directory)
    fullpaths = map(lambda name: os.path.join(directory, name), dirfiles)
    folderList = []
    for fileID, filePath in enumerate(fullpaths):
      if os.path.isdir(filePath): 
        folderList.append(dirfiles[fileID])
    return list(folderList)

  #------------------------------------------------------------------------------
  def filterParticipantInfoListFromSearchText(self, participantInfo_list, searchText):
    """
    Filters participant information list of dictionaries to keep only those participant matching the search criteria.

    :param participantInfo_list: list of dictionaries containing the information of all participants in the database (list)
    :param searchText: filter input text (string)

    :return list of dictionaries containing the information of all participants matching search criteria (list)
    """
    logging.debug('RecordingManager.filterParticipantInfoListFromSearchText')

    # Convert input search text to lower case
    ## TODO: Convert text to account for accents and other symbols
    searchText = searchText.lower()

    # Get number of participants in input list
    numParticipants = len(participantInfo_list)

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
  #
  # Read/write JSON info files
  #
  #------------------------------------------------------------------------------
  
  #------------------------------------------------------------------------------
  def readParticipantInfoFile(self, filePath):
    """
    Reads participant's information from .json file.

    :param filePath: path to JSON file (string)

    :return participant info (dict)
    """
    logging.debug('RecordingManager.readParticipantInfoFile')
    
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
    logging.debug('RecordingManager.readRecordingInfoFile')
    
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
    Writes participant's information into a .json file.

    :param filePath: path to file (string)
    :param participantInfo: participant information (dict)
    """
    logging.debug('RecordingManager.writeParticipantInfoFile')
    
    try:
      with open(filePath, "w") as outputFile:
        json.dump(participantInfo, outputFile, indent = 4)
    except:
      logging.error('Cannot write participant information into JSON file at ' + filePath)      

  #------------------------------------------------------------------------------
  def writeRecordingInfoFile(self, filePath, recordingInfo):
    """
    Writes recording's information into a .json file.

    :param filePath: path to file (string)
    :param recordingInfo: recording information (dict)
    """
    logging.debug('RecordingManager.writeRecordingInfoFile')

    try:
      with open(filePath, "w") as outputFile:
        json.dump(recordingInfo, outputFile, indent = 4)
    except:
      logging.error('Cannot write recording information into JSON file at ' + filePath)


  #------------------------------------------------------------------------------
  #
  # Get participant/recording info from ID
  #
  #------------------------------------------------------------------------------
  
  #------------------------------------------------------------------------------
  def getParticipantInfoFromID(self, participantID):
    """
    Get participant's information from participant ID.

    :param participantID: participant ID (string)

    :return participant info (dict)
    """
    logging.debug('RecordingManager.getParticipantInfoFromID')
    
    # Abort if participant ID is not valid
    if participantID == '':
      return

    # Get participant info file path
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
    logging.debug('RecordingManager.getRecordingInfoFromID')
    
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
    logging.debug('RecordingManager.getParticipantInfoFilePath')
    
    # Participant directory
    participantDirectory = os.path.join(self.rootDirectory, participantID)

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
    logging.debug('RecordingManager.getRecordingInfoFilePath')
    
    # Participant directory
    participantDirectory = os.path.join(self.rootDirectory, participantID)

    # Recording directory
    recordingDirectory = os.path.join(participantDirectory, recordingID)

    # Participant info file
    recordingInfoFilePath = os.path.join(recordingDirectory, 'Recording_Info.json')

    return recordingInfoFilePath


  #------------------------------------------------------------------------------
  #
  # Handle selected participant/recording using app parameter node
  #
  #------------------------------------------------------------------------------

  #------------------------------------------------------------------------------
  def isParticipantSelected(self):
    """
    Check if a valid participant is selected.

    :return bool: True if valid participant is selected, False otherwise
    """    
    logging.debug('RecordingManager.isParticipantSelected')
    
    # Get selected participant
    selectedParticipantID = self.getSelectedParticipantID()

    # Check valid selection
    if (selectedParticipantID == '') :
      participantSelected = False
    else:
      participantSelected = True
    return participantSelected

  #------------------------------------------------------------------------------
  def isRecordingSelected(self):
    """
    Check if a valid recording is selected.

    :return bool: True if valid recording is selected, False otherwise
    """    
    logging.debug('RecordingManager.isRecordingSelected')
    
    # Get selected recording
    selectedRecordingID = self.getSelectedRecordingID()

    # Check valid selection
    if (selectedRecordingID == '') :
      recordingSelected = False
    else:
      recordingSelected = True
    return recordingSelected

  #------------------------------------------------------------------------------
  def getSelectedParticipantID(self):
    """
    Get selected participant ID.
    """
    logging.debug('RecordingManager.getSelectedParticipantID')
    
    # Get selected participant
    selectedParticipantID = Parameters.instance.getParameterString(Parameters.SELECTED_PARTICIPANT_ID)
    return selectedParticipantID

  #------------------------------------------------------------------------------
  def setSelectedParticipantID(self, participantID):
    """
    Set selected participant ID.
    """
    logging.debug('RecordingManager.setSelectedParticipantID')
    
    # Update parameter node
    Parameters.instance.setParameter(Parameters.SELECTED_PARTICIPANT_ID, participantID) 

  #------------------------------------------------------------------------------
  def getSelectedRecordingID(self):
    """
    Get selected recording ID.
    """
    logging.debug('RecordingManager.getSelectedRecordingID')
    
    # Get selected participant
    selectedRecordingID = Parameters.instance.getParameterString(Parameters.SELECTED_RECORDING_ID)
    return selectedRecordingID

  #------------------------------------------------------------------------------
  def setSelectedRecordingID(self, recordingID):
    """
    Set selected recording ID.
    """
    logging.debug('RecordingManager.setSelectedRecordingID')
    
    # Update parameter node
    Parameters.instance.setParameter(Parameters.SELECTED_RECORDING_ID, recordingID)
  
  #------------------------------------------------------------------------------
  def getParticipantInfoFromSelection(self):
    """
    Get information for selected participant.

    :return participant info (dict)
    """
    logging.debug('RecordingManager.getParticipantInfoFromSelection')
    
    # Get selected participant
    selectedParticipantID = self.getSelectedParticipantID()

    # Get participant info from ID
    selectedParticipantInfo = self.getParticipantInfoFromID(selectedParticipantID)

    return selectedParticipantInfo

  #------------------------------------------------------------------------------
  def getRecordingInfoFromSelection(self):
    """
    Get information for selected recording.

    :return recording info (dict)
    """
    logging.debug('RecordingManager.getRecordingInfoFromSelection')
    
    # Get selected participant and recording
    selectedParticipantID = self.getSelectedParticipantID()
    selectedRecordingID = self.getSelectedRecordingID()

    # Get participant info from ID
    selectedRecordingInfo = self.getRecordingInfoFromID(selectedParticipantID, selectedRecordingID)

    return selectedRecordingInfo


  #------------------------------------------------------------------------------
  #
  # Delete participant/recording from database
  #
  #------------------------------------------------------------------------------    

  #------------------------------------------------------------------------------
  def deleteParticipant(self, participantID):
    """
    Delete participant from root directory.

    :param participantID: participant ID (string)
    """
    logging.debug('RecordingManager.deleteParticipant')

    # Abort if input ID is not valid
    if (participantID == ''):
      return

    # Participant directory
    participantDirectory = os.path.join(self.rootDirectory, participantID)

    # Delete folder
    try:
      shutil.rmtree(participantDirectory, ignore_errors=True)
    except:
      logging.error('ERROR: Participant folder could not be deleted.')

  #------------------------------------------------------------------------------
  def deleteSelectedParticipant(self):
    """
    Delete selected participant from root directory and resets selection.
    """
    logging.debug('RecordingManager.deleteSelectedParticipant')
    
    # Get selected participant
    selectedParticipantID = self.getSelectedParticipantID()

    # Delete participant
    self.deleteParticipant(selectedParticipantID)
    
    # Unselect deleted participant
    self.setSelectedParticipantID('')

  #------------------------------------------------------------------------------
  def deleteRecording(self, participantID, recordingID):
    """
    Delete recording from root directory.

    :param participantID: participant ID (string)
    :param recordingID: recording ID (string)
    """
    logging.debug('RecordingManager.deleteRecording')

    # Abort if input IDs are not valid
    if (participantID == '') or (recordingID == ''):
      return

    # Get recording directory
    participantDirectory = os.path.join(self.rootDirectory, participantID)
    recordingDirectory = os.path.join(participantDirectory, recordingID)

    # Delete folder
    try:
      shutil.rmtree(recordingDirectory, ignore_errors=True)
    except:
      logging.error('ERROR: Recording folder could not be deleted.')

  #------------------------------------------------------------------------------
  def deleteSelectedRecording(self):
    """
    Delete selected recording from root directory.
    """
    logging.debug('RecordingManager.deleteSelectedRecording')
    
    # Get selected participant and recording
    selectedParticipantID = self.getSelectedParticipantID()
    selectedRecordingID = self.getSelectedRecordingID()

    # Delete recording
    self.deleteRecording(selectedParticipantID, selectedRecordingID)
    
    # Unselect recording
    self.setSelectedRecordingID('')

  #------------------------------------------------------------------------------
  #
  # Create new participant/recording
  #
  #------------------------------------------------------------------------------    

  #------------------------------------------------------------------------------
  def createNewParticipant(self, participantName, participantSurname, participantBirthDate, participantEmail):
    """
    Adds new participant to database by generating a unique ID, creating a new folder, 
    and creating a new .json file containing participant information.

    :param participantName: participant name (string)
    :param participantSurname: participant surname (string)
    :param participantBirthDate: participant birth date (string)
    :param participantEmail: participant email (string)

    :return new participant info (dict)
    """
    logging.debug('RecordingManager.createNewParticipant')

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

    # Create participant folder
    participantDirectory = os.path.join(self.rootDirectory, str(newParticipantID))
    try:
      os.makedirs(participantDirectory)    
      logging.debug('Participant folder was created.')
    except FileExistsError:
      logging.error('New participant folder could not be created.')

    # Create participant info dictionary
    participantInfo = {}
    participantInfo['id'] = newParticipantID
    participantInfo['name'] = participantName
    participantInfo['surname'] = participantSurname
    participantInfo['birthdate'] = participantBirthDate
    participantInfo['email'] = participantEmail

    # Create participant info file
    participantInfoFilePath = self.getParticipantInfoFilePath(newParticipantID)
    self.writeParticipantInfoFile(participantInfoFilePath, participantInfo)

    # Update participant selection
    self.setSelectedParticipantID(participantInfo['id'])

    return participantInfo

  #------------------------------------------------------------------------------
  def createNewRecording(self, exerciseName, recordingDuration):
    """
    Adds new recording to database by generating a unique ID, creating a new folder, 
    and creating a new .json file containing the recording information.

    :param exerciseName: exercise name for recording (string)
    :param recordingDuration: duration of recording in seconds (float)

    :return new recording info (dict)
    """
    logging.debug('RecordingManager.createNewRecording')

    # Get selected participant and recording
    selectedParticipantID = self.getSelectedParticipantID()

    # Get existing recordings from directory
    recordingInfo_list = self.readParticipantDirectory(selectedParticipantID)

    # Get existing recording IDs
    numRecordings = len(recordingInfo_list)
    recordingID_list = []
    for recording in range(numRecordings):
      recordingID_list.append(recordingInfo_list[recording]['id'][1:])

    # Generate new recording ID (TODO: improve to ensure uniqueness)
    recordingID_array = np.array(recordingID_list).astype(int)
    try:
      maxRecordingID = np.max(recordingID_array)
    except:
      maxRecordingID = 0
    newRecordingID = str("R{:05d}".format(maxRecordingID + 1)) # leading zeros, 5 digits

    # Get current date and time
    from datetime import datetime
    dateLabel = datetime.now().strftime('%Y-%m-%d')
    timeLabel = datetime.now().strftime('%H:%M:%S')

    # Create recording folder
    participantDirectory = os.path.join(self.rootDirectory, selectedParticipantID)
    recordingDirectory = os.path.join(participantDirectory, newRecordingID)
    try:
      os.makedirs(recordingDirectory)    
      logging.debug('Recording folder was created.')
    except FileExistsError:
      logging.error('New recording folder could not be created.')

    # Create recording info dictionary
    recordingInfo = {}
    recordingInfo['id'] = newRecordingID
    recordingInfo['date'] = dateLabel
    recordingInfo['time'] = timeLabel
    recordingInfo['exercise'] = exerciseName
    recordingInfo['duration'] = f'{recordingDuration:.2f}'

    # Create recording info file
    recordingInfoFilePath = self.getRecordingInfoFilePath(selectedParticipantID, newRecordingID)
    self.writeRecordingInfoFile(recordingInfoFilePath, recordingInfo)

    # Update recording selection
    self.setSelectedRecordingID(recordingInfo['id'])

    return recordingInfo

  #------------------------------------------------------------------------------
  #
  # Edit existing participant info
  #
  #------------------------------------------------------------------------------    

  #------------------------------------------------------------------------------
  def editParticipantInfo(self, participantName, participantSurname, participantBirthDate, participantEmail):
    """
    Edit info of the selected participant in the JSON info file.

    :param participantName: new name for partipant (string)
    :param participantSurname: new surname for participant (string)
    :param participantBirthDate: new birth date for participant (string)
    :param participantEmail: new email for participant (string)
    """    
    logging.debug('RecordingManager.editParticipantInfo')
    
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

  