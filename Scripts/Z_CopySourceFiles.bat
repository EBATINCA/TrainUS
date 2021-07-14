REM Convenience script to copy Python-based code to build directory so that the application
REM does not have to be built during development when no C++ component is changed

@call %~dp0\CommonVars.bat

copy /Y %TRAINUS_SOURCE_DIR%\Modules\Home\Home.py   %SLICER_BIN_DIR_REL_X64%\lib\TrainUS-4.13\qt-scripted-modules
copy /Y %TRAINUS_SOURCE_DIR%\Modules\Home\Resources\UI\*.ui %SLICER_BIN_DIR_REL_X64%\lib\TrainUS-4.13\qt-scripted-modules\Resources\UI
copy /Y %TRAINUS_SOURCE_DIR%\Modules\Home\Resources\Home.qss %SLICER_BIN_DIR_REL_X64%\lib\TrainUS-4.13\qt-scripted-modules\Resources

copy /Y %TRAINUS_SOURCE_DIR%\Modules\Home\Home.py   %SLICER_BIN_DIR_DBG_X64%\lib\TrainUS-4.13\qt-scripted-modules
copy /Y %TRAINUS_SOURCE_DIR%\Modules\Home\Resources\UI\*.ui %SLICER_BIN_DIR_DBG_X64%\lib\TrainUS-4.13\qt-scripted-modules\Resources\UI
copy /Y %TRAINUS_SOURCE_DIR%\Modules\Home\Resources\Home.qss %SLICER_BIN_DIR_DBG_X64%\lib\TrainUS-4.13\qt-scripted-modules\Resources
