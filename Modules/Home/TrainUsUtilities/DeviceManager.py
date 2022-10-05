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

    # Get list of registered devices
    listOfRegisteredDevices = self.getListOfRegisteredDevices()

    # Display
    print('\n>>>>>DeviceManager.readMainDirectory<<<<<<<<<<<<')
    print('\nDirectory: ', self.mainDirectory)
    print('\nDevices in directory: ', listOfRegisteredDevices)
  
  #------------------------------------------------------------------------------
  #
  # Read/write JSON info files
  #
  #------------------------------------------------------------------------------
  
  #------------------------------------------------------------------------------
  def getDictionaryFromJSONFile(self, filePath):
    """
    Get Python dictionary from .json file.

    :param filePath: path to JSON file (string)

    :return file content (dict)
    """
    logging.debug('DeviceManager.getDictionaryFromJSONFile')
    
    try:
      with open(filePath, 'r') as inputFile:
        outputDictionary =  json.loads(inputFile.read())
    except:
      logging.error('Cannot read JSON file: ' + filePath)
      outputDictionary = None
    return outputDictionary

  #------------------------------------------------------------------------------
  #
  # Get device info from ID
  #
  #------------------------------------------------------------------------------
  
  #------------------------------------------------------------------------------
  def getDeviceInfoFilePath(self):
    """
    Get path to device's information JSON file.

    :param deviceID: device ID (string)

    :return device info (dict)
    """
    logging.debug('DeviceManager.getDeviceInfoFilePath')
    
    # Device directory
    deviceInfoFilePath = os.path.join(self.mainDirectory, 'Device_Info.json')

    return deviceInfoFilePath

  #------------------------------------------------------------------------------
  def getRegisteredDevicesInfo(self):
    # Get JSON file path
    deviceListFilePath = self.getDeviceInfoFilePath()

    # Read JSON file content
    deviceListDictionary = self.getDictionaryFromJSONFile(deviceListFilePath)
    if not deviceListDictionary:
      return None

    return deviceListDictionary

  #------------------------------------------------------------------------------
  def getListOfRegisteredDevices(self):
    # Read registered devices info from JSON file
    deviceListDictionary = self.getRegisteredDevicesInfo()

    # Get list of registered devices
    listOfRegisteredDevices = list(deviceListDictionary.keys())

    return listOfRegisteredDevices

  #------------------------------------------------------------------------------
  def getDeviceInfoFromName(self, deviceName):
    # Get list of registered device names
    listOfRegisteredDevices = self.getListOfRegisteredDevices()
    if not listOfRegisteredDevices:
      logging.error('No registered devices were found')
      return

    # Check if input device is registered
    if deviceName not in listOfRegisteredDevices:
      logging.error('Input device with name %s is not registered. Device information cannot be retrieved.' % deviceName)
      return

    # Get registered devices info
    deviceListDictionary = self.getRegisteredDevicesInfo()    

    # Get device info
    deviceInfoDictionary = deviceListDictionary[deviceName]

    return deviceInfoDictionary

  #------------------------------------------------------------------------------
  def getListOfRegisteredUltrasoundDevices(self):
    # Get list of registered devices
    listOfRegisteredDevices = self.getListOfRegisteredDevices()

    # Get registered devices info
    deviceListDictionary = self.getRegisteredDevicesInfo()  

    # Check device type
    listOfRegisteredUltrasoundDevices = list()
    for deviceName in listOfRegisteredDevices:
      # Get device info
      deviceInfoDictionary = deviceListDictionary[deviceName]
      # Get device type: tracker or ultrasound
      deviceType = deviceInfoDictionary['device type']
      # Populate list of ultrasound devices
      if deviceType == 'ultrasound':
        listOfRegisteredUltrasoundDevices.append(deviceName)

    return listOfRegisteredUltrasoundDevices

  #------------------------------------------------------------------------------
  def getListOfRegisteredTrackerDevices(self):
    # Get list of registered devices
    listOfRegisteredDevices = self.getListOfRegisteredDevices()

    # Get registered devices info
    deviceListDictionary = self.getRegisteredDevicesInfo()  

    # Check device type
    listOfRegisteredTrackerDevices = list()
    for deviceName in listOfRegisteredDevices:
      # Get device info
      deviceInfoDictionary = deviceListDictionary[deviceName]
      # Get device type: tracker or ultrasound
      deviceType = deviceInfoDictionary['device type']
      # Populate list of tracker devices
      if deviceType == 'tracker':
        listOfRegisteredTrackerDevices.append(deviceName)

    return listOfRegisteredTrackerDevices


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
    selectedUltrasoundDeviceInfo = self.getDeviceInfoFromName(selectedUltrasoundDevice)

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
      configFilePath = os.path.join(self.mainDirectory, selectedUltrasoundDeviceInfo['plus config file'])
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
      plusServerPath = selectedUltrasoundDeviceInfo['plus server']
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
      plusServerLauncherPath = selectedUltrasoundDeviceInfo['plus launcher']
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
    selectedTrackerDeviceInfo = self.getDeviceInfoFromName(selectedTrackerDevice)

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
      configFilePath = os.path.join(self.mainDirectory, selectedTrackerDeviceInfo['plus config file'])
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
      plusServerPath = selectedTrackerDeviceInfo['plus server']
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
      plusServerLauncherPath = selectedTrackerDeviceInfo['plus launcher']
    else:
      plusServerLauncherPath = ''

    return plusServerLauncherPath
