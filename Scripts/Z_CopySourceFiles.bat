REM Convenience script to copy Python-based code to build directory so that the application
REM does not have to be built during development when no C++ component is changed

@call %~dp0\CommonVars.bat

copy /Y %TRAINUS_SOURCE_DIR%\Modules\Home\Home.py %SLICER_BIN_DIR_REL_X64%\lib\TrainUS-5.0\qt-scripted-modules
copy /Y %TRAINUS_SOURCE_DIR%\Modules\Home\Resources\UI\*.ui %SLICER_BIN_DIR_REL_X64%\lib\TrainUS-5.0\qt-scripted-modules\Resources\UI
copy /Y %TRAINUS_SOURCE_DIR%\Modules\Home\Resources\Home.qss %SLICER_BIN_DIR_REL_X64%\lib\TrainUS-5.0\qt-scripted-modules\Resources
copy /Y %TRAINUS_SOURCE_DIR%\Modules\TrainUS\TrainUS.py %SLICER_BIN_DIR_REL_X64%\lib\TrainUS-5.0\qt-scripted-modules
copy /Y %TRAINUS_SOURCE_DIR%\Modules\TrainUS\Resources\UI\*.ui %SLICER_BIN_DIR_REL_X64%\lib\TrainUS-5.0\qt-scripted-modules\Resources\UI
copy /Y %TRAINUS_SOURCE_DIR%\Modules\TrainUS\Resources\TrainUS.qss %SLICER_BIN_DIR_REL_X64%\lib\TrainUS-5.0\qt-scripted-modules\Resources
copy /Y %TRAINUS_SOURCE_DIR%\Modules\Evaluator\Evaluator.py %SLICER_BIN_DIR_REL_X64%\lib\TrainUS-5.0\qt-scripted-modules
copy /Y %TRAINUS_SOURCE_DIR%\Modules\Evaluator\Resources\UI\Evaluator.ui %SLICER_BIN_DIR_REL_X64%\lib\TrainUS-5.0\qt-scripted-modules\Resources\UI
copy /Y %TRAINUS_SOURCE_DIR%\Modules\ToolPivotCalibration\ToolPivotCalibration.py %SLICER_BIN_DIR_REL_X64%\lib\TrainUS-5.0\qt-scripted-modules
copy /Y %TRAINUS_SOURCE_DIR%\Modules\ToolPivotCalibration\Resources\UI\ToolPivotCalibration.ui %SLICER_BIN_DIR_REL_X64%\lib\TrainUS-5.0\qt-scripted-modules\Resources\UI
copy /Y %TRAINUS_SOURCE_DIR%\Modules\ToolTrackingStatus\ToolTrackingStatus.py %SLICER_BIN_DIR_REL_X64%\lib\TrainUS-5.0\qt-scripted-modules
copy /Y %TRAINUS_SOURCE_DIR%\Modules\ToolTrackingStatus\Resources\UI\ToolTrackingStatus.ui %SLICER_BIN_DIR_REL_X64%\lib\TrainUS-5.0\qt-scripted-modules\Resources\UI
copy /Y %TRAINUS_SOURCE_DIR%\Modules\UltrasoundDisplaySettings\UltrasoundDisplaySettings.py %SLICER_BIN_DIR_REL_X64%\lib\TrainUS-5.0\qt-scripted-modules
copy /Y %TRAINUS_SOURCE_DIR%\Modules\UltrasoundDisplaySettings\Resources\UI\UltrasoundDisplaySettings.ui %SLICER_BIN_DIR_REL_X64%\lib\TrainUS-5.0\qt-scripted-modules\Resources\UI
copy /Y %TRAINUS_SOURCE_DIR%\Modules\UltrasoundProbeCalibration\UltrasoundProbeCalibration.py %SLICER_BIN_DIR_REL_X64%\lib\TrainUS-5.0\qt-scripted-modules
copy /Y %TRAINUS_SOURCE_DIR%\Modules\UltrasoundProbeCalibration\Resources\UI\UltrasoundProbeCalibration.ui %SLICER_BIN_DIR_REL_X64%\lib\TrainUS-5.0\qt-scripted-modules\Resources\UI

copy /Y %TRAINUS_SOURCE_DIR%\Modules\Home\Home.py %SLICER_BIN_DIR_DBG_X64%\lib\TrainUS-5.0\qt-scripted-modules
copy /Y %TRAINUS_SOURCE_DIR%\Modules\Home\Resources\UI\*.ui %SLICER_BIN_DIR_DBG_X64%\lib\TrainUS-5.0\qt-scripted-modules\Resources\UI
copy /Y %TRAINUS_SOURCE_DIR%\Modules\Home\Resources\Home.qss %SLICER_BIN_DIR_DBG_X64%\lib\TrainUS-5.0\qt-scripted-modules\Resources
copy /Y %TRAINUS_SOURCE_DIR%\Modules\TrainUS\TrainUS.py %SLICER_BIN_DIR_DBG_X64%\lib\TrainUS-5.0\qt-scripted-modules
copy /Y %TRAINUS_SOURCE_DIR%\Modules\TrainUS\Resources\UI\*.ui %SLICER_BIN_DIR_DBG_X64%\lib\TrainUS-5.0\qt-scripted-modules\Resources\UI
copy /Y %TRAINUS_SOURCE_DIR%\Modules\TrainUS\Resources\TrainUS.qss %SLICER_BIN_DIR_DBG_X64%\lib\TrainUS-5.0\qt-scripted-modules\Resources
copy /Y %TRAINUS_SOURCE_DIR%\Modules\Evaluator\Evaluator.py %SLICER_BIN_DIR_DBG_X64%\lib\TrainUS-5.0\qt-scripted-modules
copy /Y %TRAINUS_SOURCE_DIR%\Modules\Evaluator\Resources\UI\Evaluator.ui %SLICER_BIN_DIR_DBG_X64%\lib\TrainUS-5.0\qt-scripted-modules\Resources\UI
copy /Y %TRAINUS_SOURCE_DIR%\Modules\ToolPivotCalibration\ToolPivotCalibration.py %SLICER_BIN_DIR_DBG_X64%\lib\TrainUS-5.0\qt-scripted-modules
copy /Y %TRAINUS_SOURCE_DIR%\Modules\ToolPivotCalibration\Resources\UI\ToolPivotCalibration.ui %SLICER_BIN_DIR_DBG_X64%\lib\TrainUS-5.0\qt-scripted-modules\Resources\UI
copy /Y %TRAINUS_SOURCE_DIR%\Modules\ToolTrackingStatus\ToolTrackingStatus.py %SLICER_BIN_DIR_DBG_X64%\lib\TrainUS-5.0\qt-scripted-modules
copy /Y %TRAINUS_SOURCE_DIR%\Modules\ToolTrackingStatus\Resources\UI\ToolTrackingStatus.ui %SLICER_BIN_DIR_DBG_X64%\lib\TrainUS-5.0\qt-scripted-modules\Resources\UI
copy /Y %TRAINUS_SOURCE_DIR%\Modules\UltrasoundDisplaySettings\UltrasoundDisplaySettings.py %SLICER_BIN_DIR_DBG_X64%\lib\TrainUS-5.0\qt-scripted-modules
copy /Y %TRAINUS_SOURCE_DIR%\Modules\UltrasoundDisplaySettings\Resources\UI\UltrasoundDisplaySettings.ui %SLICER_BIN_DIR_DBG_X64%\lib\TrainUS-5.0\qt-scripted-modules\Resources\UI
copy /Y %TRAINUS_SOURCE_DIR%\Modules\UltrasoundProbeCalibration\UltrasoundProbeCalibration.py %SLICER_BIN_DIR_DBG_X64%\lib\TrainUS-5.0\qt-scripted-modules
copy /Y %TRAINUS_SOURCE_DIR%\Modules\UltrasoundProbeCalibration\Resources\UI\UltrasoundProbeCalibration.ui %SLICER_BIN_DIR_DBG_X64%\lib\TrainUS-5.0\qt-scripted-modules\Resources\UI
