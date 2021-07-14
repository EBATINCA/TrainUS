rem @echo off

set DEVEL_DIR=e:\t

REM Directory where this file is located
set BUILD_SCRIPT_DIR=%~dp0

SET SVN_EXE="c:\Program Files\SlikSvn\bin\svn.exe"
SET SVNVERSION_EXE="c:\Program Files\SlikSvn\bin\svnversion.exe"
set GIT_EXE="c:\Program Files\Git\bin\git.exe"
set PATCH_EXE="c:\Program Files\Git\usr\bin\patch.exe"
set CMAKE_EXE="c:\Program Files\CMake\bin\cmake.exe"
set CPACK_EXE="c:\Program Files\CMake\bin\cpack.exe"
set CTEST_EXE="c:\Program Files\CMake\bin\ctest.exe"

set DOT_EXE="C:/Program Files (x86)/Graphviz2.38/bin/dot.exe"
set DOXYGEN_EXE="C:/Program Files/doxygen/bin/doxygen.exe"

set QT5_DIR_X64=C:/Qt/5.15.1/5.15.1/msvc2019_64/lib/cmake/Qt5

set CMAKE_GENERATOR_X64="Visual Studio 16 2019"

set MSBUILD_EXE="c:\Program Files (x86)\Microsoft Visual Studio\2019\Community\MSBuild\Current\Bin\MSBuild.exe"

set TRAINUS_SOURCE_DIR=%DEVEL_DIR%\TrainUS
set TRAINUS_SUPERBUILD_BIN_DIR_DBG_X64=%DEVEL_DIR%\tD
set TRAINUS_SUPERBUILD_BIN_DIR_REL_X64=%DEVEL_DIR%\tR
set SLICER_BIN_DIR_DBG_X64=%TRAINUS_SUPERBUILD_BIN_DIR_DBG_X64%\Slicer-build
set SLICER_BIN_DIR_REL_X64=%TRAINUS_SUPERBUILD_BIN_DIR_REL_X64%\Slicer-build

set PATH=%PATH%;c:\Program Files\Git\bin;c:\Program Files\Git\usr\bin
