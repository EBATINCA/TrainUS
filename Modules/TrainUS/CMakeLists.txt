#-----------------------------------------------------------------------------
set(MODULE_NAME TrainUS)

#-----------------------------------------------------------------------------
set(MODULE_PYTHON_SCRIPTS
  ${MODULE_NAME}.py
  ${MODULE_NAME}Lib/__init__.py
  ${MODULE_NAME}Lib/TrainUSParameters.py
  )

set(MODULE_PYTHON_RESOURCES
  Resources/Icons/${MODULE_NAME}.png
  Resources/Icons/Gears.png
  Resources/UI/${MODULE_NAME}.ui
  Resources/UI/Settings.ui  
  Resources/TrainUS.qss
  Resources/DeviceConfig/Device_Info.json
  Resources/DeviceConfig/Ultrasound_TelemedMicrUsLinearProbe_PlusConfigFile.xml
  Resources/DeviceConfig/Ultrasound_TelemedMicrUsConvexProbe_PlusConfigFile.xml
  Resources/DeviceConfig/Ultrasound_SimulatorLinearProbe_PlusConfigFile.xml
  Resources/DeviceConfig/Ultrasound_SimulatorConvexProbe_PlusConfigFile.xml
  Resources/DeviceConfig/Tracker_trakSTAR3DGuidance_PlusConfigFile.xml
  Resources/DeviceConfig/Tracker_Simulator_PlusConfigFile.xml
  Resources/DeviceConfig/Tracker_OptitrackDuo_PlusConfigFile.xml
  Resources/DeviceConfig/Tracker_OptitrackDuo_ProjectFile.ttp
  Resources/DeviceConfig/UltrasoundRecordingLinear.mha
  Resources/DeviceConfig/UltrasoundRecordingConvex.mha
  )

slicerFunctionAddPythonQtResources(MODULE_PYTHON_QRC_RESOURCES
  Resources/TrainUSResources.qrc
  )

#-----------------------------------------------------------------------------
slicerMacroBuildScriptedModule(
  NAME ${MODULE_NAME}
  SCRIPTS ${MODULE_PYTHON_SCRIPTS}  ${MODULE_PYTHON_QRC_RESOURCES}
  RESOURCES ${MODULE_PYTHON_RESOURCES}
  WITH_GENERIC_TESTS
  )

#-----------------------------------------------------------------------------
if(BUILD_TESTING)

  # Register the unittest subclass in the main script as a ctest.
  # Note that the test will also be available at runtime.
  slicer_add_python_unittest(SCRIPT ${MODULE_NAME}.py)

  # Additional build-time testing
  add_subdirectory(Testing)
endif()
