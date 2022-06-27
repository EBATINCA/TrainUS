#-----------------------------------------------------------------------------
set(MODULE_NAME Home)

#-----------------------------------------------------------------------------
set(MODULE_PYTHON_SCRIPTS
  ${MODULE_NAME}.py
  Widgets/__init__.py
  Widgets/Configuration.py
  Widgets/Evaluation.py
  Widgets/HardwareSelection.py
  Widgets/ParticipantSelection.py
  Widgets/PlugAndPlay.py
  Widgets/ReviewSelection.py
  Widgets/TrainingSession.py
  TrainUsUtilities/__init__.py
  TrainUsUtilities/RecordingManager.py
  TrainUsUtilities/DeviceManager.py
  TrainUsUtilities/LayoutUtils.py
  TrainUsUtilities/MetricCalculationUtils.py
  TrainUsUtilities/PlaybackPlotChartUtils.py
  TrainUsUtilities/SequenceBrowserUtils.py
  )

set(MODULE_PYTHON_RESOURCES
  Resources/Home.qss  
  Resources/Icons/${MODULE_NAME}.png
  Resources/Logo/TrainUS_Logo.png
  Resources/UI/${MODULE_NAME}.ui
  Resources/UI/Configuration.ui
  Resources/UI/Evaluation.ui
  Resources/UI/HardwareSelection.ui
  Resources/UI/ParticipantSelection.ui
  Resources/UI/PlugAndPlay.ui
  Resources/UI/ReviewSelection.ui
  Resources/UI/TrainingSession.ui
  Resources/UI/LanguageFile_English.json
  Resources/UI/LanguageFile_Spanish.json
  )

slicerFunctionAddPythonQtResources(MODULE_PYTHON_QRC_RESOURCES
  Resources/HomeResources.qrc
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
