from __main__ import vtk, qt, ctk, slicer
import logging
import os
import json

# TrainUS parameters
import TrainUSLib.TrainUSParameters as Parameters

#------------------------------------------------------------------------------
#
# DeviceManager
#
#------------------------------------------------------------------------------
class DeviceManager():
  """
  TODO: Verbose description abotu the purpose of this class
  """
  def __init__(self):
  	# Main directory
    self.mainDirectory = ''

  #------------------------------------------------------------------------------
  #
  # Read main directory
  #
  #------------------------------------------------------------------------------
  
  #------------------------------------------------------------------------------
  def setMainDirectory(self, dataPath):
    """
    Sets the directory of the database where devices' info is stored.
    """
    logging.debug('DeviceManager.setMainDirectory')

    self.mainDirectory = dataPath

  #------------------------------------------------------------------------------
  def getMainDirectory(self):
    """
    Gets the directory of the database where devices' info is stored.

    :return directory to main directory (string)
    """
    logging.debug('DeviceManager.getMainDirectory')

    return self.mainDirectory

  #------------------------------------------------------------------------------
  def readMainDirectory(self):
    """
    Reads all the files in the main directory to get the list of devices.

    :return list of dictionaries containing the information of all available devices (list)
    """
    logging.debug('DeviceManager.readMainDirectory')

    # Get list of device IDs
    deviceID_list = self.getListOfFoldersInDirectory(self.mainDirectory)

    # Get individial device info and store in list of dictionaries
    deviceInfo_list = list() # list of dictionaries
    for deviceID in deviceID_list:
      # Device info file path
      deviceInfoFilePath = self.getDeviceInfoFilePath(deviceID)
      # Get device info
      deviceInfo = self.readDeviceInfoFile(deviceInfoFilePath)
      deviceInfo_list.append(deviceInfo)

    # Display
    print('\n>>>>>DeviceManager.readMainDirectory<<<<<<<<<<<<')
    print('\nDirectory: ', self.mainDirectory)
    print('\nDevices in directory: ', deviceID_list)
    print('\nInfo JSON: ', deviceInfo_list)

    return deviceInfo_list

  #------------------------------------------------------------------------------
  def getListOfFoldersInDirectory(self, directory):
    """
    Gets list of folders contained in input directory.

    :param directory: input directory (string)

    :return list of folder names (list)
    """
    logging.debug('DeviceManager.getListOfFoldersInDirectory')

    dirfiles = os.listdir(directory)
    fullpaths = map(lambda name: os.path.join(directory, name), dirfiles)
    folderList = []
    for fileID, filePath in enumerate(fullpaths):
      if os.path.isdir(filePath): 
        folderList.append(dirfiles[fileID])
    return list(folderList)

  
  #------------------------------------------------------------------------------
  #
  # Read/write JSON info files
  #
  #------------------------------------------------------------------------------
  
  #------------------------------------------------------------------------------
  def readDeviceInfoFile(self, filePath):
    """
    Reads device's information from .json file.

    :param filePath: path to JSON file (string)

    :return device info (dict)
    """
    logging.debug('DeviceManager.readDeviceInfoFile')
    
    try:
      with open(filePath, 'r') as inputFile:
        deviceInfo =  json.loads(inputFile.read())
    except:
      logging.error('Cannot read device information from JSON file at ' + filePath)
      deviceInfo = None
    return deviceInfo


  #------------------------------------------------------------------------------
  #
  # Get device info from ID
  #
  #------------------------------------------------------------------------------
  
  #------------------------------------------------------------------------------
  def getDeviceInfoFromID(self, deviceID):
    """
    Get device's information from device ID.

    :param deviceID: device ID (string)

    :return device info (dict)
    """
    logging.debug('DeviceManager.getDeviceInfoFromID')
    
    # Abort if device ID is not valid
    if deviceID == '' or deviceID == 'None':
      return

    # Get device info file path
    deviceInfoFilePath = self.getDeviceInfoFilePath(deviceID)
    
    # Read device info
    deviceInfo = self.readDeviceInfoFile(deviceInfoFilePath)

    return deviceInfo

  #------------------------------------------------------------------------------
  def getDeviceInfoFilePath(self, deviceID):
    """
    Get path to device's information JSON file.

    :param deviceID: device ID (string)

    :return device info (dict)
    """
    logging.debug('DeviceManager.getDeviceInfoFilePath')
    
    # Device directory
    deviceDirectory = os.path.join(self.mainDirectory, deviceID)

    # Device info file
    deviceInfoFilePath = os.path.join(deviceDirectory, 'Device_Info.json')

    return deviceInfoFilePath


  #------------------------------------------------------------------------------
  #
  # Ultrasound device
  #
  #------------------------------------------------------------------------------

  #------------------------------------------------------------------------------
  def isUltrasoundDeviceSelected(self):
    """
    Check if a valid ultrasound device is selected.

    :return bool: True if valid ultrasound device is selected, False otherwise
    """    
    logging.debug('DeviceManager.isUltrasoundDeviceSelected')
    
    # Get selected ultrasound device
    selectedUltrasoundDeviceLabel = self.getSelectedUltrasoundDevice()

    # Check valid selection
    if (selectedUltrasoundDeviceLabel == '') or (selectedUltrasoundDeviceLabel == 'None'):
      ultrasoundDeviceSelected = False
    else:
      ultrasoundDeviceSelected = True
    return ultrasoundDeviceSelected

  #------------------------------------------------------------------------------
  def getSelectedUltrasoundDevice(self):
    """
    Get selected ultrasound device.
    """
    logging.debug('DeviceManager.getSelectedUltrasoundDevice')
    
    # Get selected ultrasound device
    selectedUltrasoundDevice = Parameters.instance.getParameterString(Parameters.SELECTED_ULTRASOUND)
    return selectedUltrasoundDevice

  #------------------------------------------------------------------------------
  def setSelectedUltrasoundDevice(self, deviceLabel):
    """
    Set selected ultrasound device.
    """
    logging.debug('DeviceManager.setSelectedUltrasoundDevice')

    # Update parameter node
    Parameters.instance.setParameter(Parameters.SELECTED_ULTRASOUND, deviceLabel)

  #------------------------------------------------------------------------------
  def getUltrasoundDeviceInfoFromSelection(self):
    """
    Get information for selected ultrasound device.

    :return ultrasound device info (dict)
    """
    logging.debug('DeviceManager.getUltrasoundDeviceInfoFromSelection')
    
    # Get selected device
    selectedUltrasoundDevice = self.getSelectedUltrasoundDevice()

    # Get device info from ID
    selectedUltrasoundDeviceInfo = self.getDeviceInfoFromID(selectedUltrasoundDevice)

    return selectedUltrasoundDeviceInfo

  #------------------------------------------------------------------------------
  def getUltrasoundDeviceConfigFilePathFromSelection(self):
    """
    Get config file path for selected ultrasound device.

    :return config file path (string)
    """
    logging.debug('DeviceManager.getUltrasoundDeviceConfigFilePathFromSelection')
    
    # Get selected device
    selectedUltrasoundDevice = self.getSelectedUltrasoundDevice()

    # Get device info from ID
    selectedUltrasoundDeviceInfo = self.getUltrasoundDeviceInfoFromSelection()

    # Get config file path
    if selectedUltrasoundDeviceInfo:
      devicePath = os.path.join(self.mainDirectory, selectedUltrasoundDevice)
      configFilePath = os.path.join(devicePath, selectedUltrasoundDeviceInfo['config'])
    else:
      configFilePath = ''

    return configFilePath

  #------------------------------------------------------------------------------
  def getUltrasoundDevicePlusServerPathFromSelection(self):
    """
    Get Plus server path for selected ultrasound device.

    :return plus server path (string)
    """
    logging.debug('DeviceManager.getUltrasoundDevicePlusServerPathFromSelection')
    
    # Get selected device
    selectedUltrasoundDevice = self.getSelectedUltrasoundDevice()

    # Get device info from ID
    selectedUltrasoundDeviceInfo = self.getUltrasoundDeviceInfoFromSelection()

    # Get config file path
    if selectedUltrasoundDeviceInfo:
      devicePath = os.path.join(self.mainDirectory, selectedUltrasoundDevice)
      plusServerPath = os.path.join(devicePath, selectedUltrasoundDeviceInfo['plus server'])
    else:
      plusServerPath = ''

    return plusServerPath

  #------------------------------------------------------------------------------
  def getUltrasoundDevicePlusServerLauncherPathFromSelection(self):
    """
    Get Plus server path for selected ultrasound device.

    :return plus server path (string)
    """
    logging.debug('DeviceManager.getUltrasoundDevicePlusServerLauncherPathFromSelection')
    
    # Get selected device
    selectedUltrasoundDevice = self.getSelectedUltrasoundDevice()

    # Get device info from ID
    selectedUltrasoundDeviceInfo = self.getUltrasoundDeviceInfoFromSelection()

    # Get config file path
    if selectedUltrasoundDeviceInfo:
      devicePath = os.path.join(self.mainDirectory, selectedUltrasoundDevice)
      plusServerLauncherPath = os.path.join(devicePath, selectedUltrasoundDeviceInfo['plus launcher'])
    else:
      plusServerLauncherPath = ''

    return plusServerLauncherPath


    

  #------------------------------------------------------------------------------
  #
  # Tracker device
  #
  #------------------------------------------------------------------------------

  #------------------------------------------------------------------------------
  def isTrackerDeviceSelected(self):
    """
    Check if a valid tracker device is selected.

    :return bool: True if valid tracker device is selected, False otherwise
    """    
    logging.debug('DeviceManager.isTrackerDeviceSelected')
    
    # Get selected tracker device
    selectedTrackerDeviceLabel = self.getSelectedTrackerDevice()

    # Check valid selection
    if (selectedTrackerDeviceLabel == '') or (selectedTrackerDeviceLabel == 'None'):
      trackerDeviceSelected = False
    else:
      trackerDeviceSelected = True
    return trackerDeviceSelected

  #------------------------------------------------------------------------------
  def getSelectedTrackerDevice(self):
    """
    Get selected tracker device.
    """
    logging.debug('DeviceManager.getSelectedTrackerDevice')

    # Get selected tracker device
    selectedTrackerDevice = Parameters.instance.getParameterString(Parameters.SELECTED_TRACKER)
    return selectedTrackerDevice

  #------------------------------------------------------------------------------
  def setSelectedTrackerDevice(self, deviceLabel):
    """
    Set selected tracker device.
    """
    logging.debug('DeviceManager.setSelectedTrackerDevice')
    
    # Update parameter node
    Parameters.instance.setParameter(Parameters.SELECTED_TRACKER, deviceLabel)
    
  #------------------------------------------------------------------------------
  def getTrackerDeviceInfoFromSelection(self):
    """
    Get information for selected tracker device.

    :return tracker device info (dict)
    """
    logging.debug('DeviceManager.getTrackerDeviceInfoFromSelection')
    
    # Get selected device
    selectedTrackerDevice = self.getSelectedTrackerDevice()

    # Get device info from ID
    selectedTrackerDeviceInfo = self.getDeviceInfoFromID(selectedTrackerDevice)

    return selectedTrackerDeviceInfo

  #------------------------------------------------------------------------------
  def getTrackerDeviceConfigFilePathFromSelection(self):
    """
    Get config file path for selected tracker device.

    :return config file path (string)
    """
    logging.debug('DeviceManager.getTrackerDeviceConfigFilePathFromSelection')
    
    # Get selected device
    selectedTrackerDevice = self.getSelectedTrackerDevice()

    # Get device info from ID
    selectedTrackerDeviceInfo = self.getTrackerDeviceInfoFromSelection()

    # Get config file path
    if selectedTrackerDeviceInfo:
      devicePath = os.path.join(self.mainDirectory, selectedTrackerDevice)
      configFilePath = os.path.join(devicePath, selectedTrackerDeviceInfo['config'])
    else:
      configFilePath = ''

    return configFilePath

  #------------------------------------------------------------------------------
  def getTrackerDevicePlusServerPathFromSelection(self):
    """
    Get Plus server path for selected tracker device.

    :return plus server path (string)
    """
    logging.debug('DeviceManager.getTrackerDevicePlusServerPathFromSelection')
    
    # Get selected device
    selectedTrackerDevice = self.getSelectedTrackerDevice()

    # Get device info from ID
    selectedTrackerDeviceInfo = self.getTrackerDeviceInfoFromSelection()

    # Get config file path
    if selectedTrackerDeviceInfo:
      devicePath = os.path.join(self.mainDirectory, selectedTrackerDevice)
      plusServerPath = os.path.join(devicePath, selectedTrackerDeviceInfo['plus server'])
    else:
      plusServerPath = ''

    return plusServerPath

  #------------------------------------------------------------------------------
  def getTrackerDevicePlusServerLauncherPathFromSelection(self):
    """
    Get Plus server path for selected tracker device.

    :return plus server path (string)
    """
    logging.debug('DeviceManager.getTrackerDevicePlusServerLauncherPathFromSelection')
    
    # Get selected device
    selectedTrackerDevice = self.getSelectedTrackerDevice()

    # Get device info from ID
    selectedTrackerDeviceInfo = self.getTrackerDeviceInfoFromSelection()

    # Get config file path
    if selectedTrackerDeviceInfo:
      devicePath = os.path.join(self.mainDirectory, selectedTrackerDevice)
      plusServerLauncherPath = os.path.join(devicePath, selectedTrackerDeviceInfo['plus launcher'])
    else:
      plusServerLauncherPath = ''

    return plusServerLauncherPath
