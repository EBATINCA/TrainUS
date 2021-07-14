@call CommonVars.bat
time /t

set BIN_DIR=%TRAINUS_SUPERBUILD_BIN_DIR_REL_X64%

echo Build started (%BIN_DIR%)
mkdir %BIN_DIR%
cd /d %BIN_DIR%
%CMAKE_EXE% %TRAINUS_SOURCE_DIR% -G %CMAKE_GENERATOR_X64% -DQt5_DIR:PATH=%QT5_DIR_X64%
%CTEST_EXE% -D Experimental -C Release

time /t
echo Build finished (%BIN_DIR%)
pause
