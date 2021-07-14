@call CommonVars.bat

REM Return code is 0 on success and >0 if something failed
SET RETURN_CODE=0

REM First we need to build a Release version

cd /d %SLICER_BIN_DIR_REL_X64%
%MSBUILD_EXE% ALL_BUILD.vcxproj /p:Configuration=Release
IF ERRORLEVEL 1 GOTO BUILDFAILED

:PACKAGE
REM Build the package
%CPACK_EXE% --config ./CPackConfig.cmake
IF ERRORLEVEL 1  GOTO PACKAGINGFAILED
ECHO Packaging DONE

:SUCCESS
ECHO Package generation is successfully completed.
pause
exit /b 0

:BUILDFAILED
ECHO ERROR: Build failed...
pause
exit /b 1

:PACKAGINGFAILED
ECHO ERROR: Package generation failed...
pause
exit /b 2
