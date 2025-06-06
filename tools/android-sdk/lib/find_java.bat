@echo off
rem Copyright (C) 2007 The Android Open Source Project
rem
rem Licensed under the Apache License, Version 2.0 (the "License");
rem you may not use this file except in compliance with the License.
rem You may obtain a copy of the License at
rem
rem      http://www.apache.org/licenses/LICENSE-2.0
rem
rem Unless required by applicable law or agreed to in writing, software
rem distributed under the License is distributed on an "AS IS" BASIS,
rem WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
rem See the License for the specific language governing permissions and
rem limitations under the License.

rem This script is called by the other batch files to find a suitable Java.exe
rem to use. The script changes the "java_exe" env variable. The variable
rem is left unset if Java.exe was not found.

rem Useful links:
rem Command-line reference:
rem   http://technet.microsoft.com/en-us/library/bb490890.aspx

rem Query whether this system is 32-bit or 64-bit
rem Note: Some users report that reg.exe is missing on their machine, so we
rem check for that first, as we'd like to use it if we can.
set sys_32=%SYSTEMROOT%\system32
if exist %sys_32%\reg.exe (
    rem This first-pass solution returns the correct architecture even if you
    rem call this .bat file from a 32-bit process.
    rem See also: http://stackoverflow.com/a/24590583/1299302
    %sys_32%\reg query "HKLM\Hardware\Description\System\CentralProcessor\0"^
    | %sys_32%\find /i "x86" > NUL && set arch_ext=32|| set arch_ext=64
) else (
    rem This fallback approach is simpler, but may misreport your architecture as
    rem 32-bit if running from a 32-bit process. Still, it should serve to help
    rem our users without reg.exe, at least.
    if "%PROCESSOR_ARCHITECTURE%" == "x86" (set arch_ext=32) else (set arch_ext=64)
)

rem Check we have a valid Java.exe in the path. The return code will
rem be 0 if the command worked or 1 if the exec failed (program not found).
for /f "delims=" %%a in ('"%~dps0\find_java%arch_ext%.exe" -s -m 1.8') do set java_exe=%%a
if not defined java_exe goto :CheckFailed

:SearchJavaW
rem Check if we can find a javaw.exe at the same location than java.exe.
rem If that doesn't work, just fall back on the java.exe we just found.
for /f "delims=" %%a in ('"%~dps0\find_java%arch_ext%.exe" -s -w -m 1.8') do set javaw_exe=%%a
if not exist "%javaw_exe%" set javaw_exe=%java_exe%
goto :EOF


:CheckFailed
echo.
echo ERROR: No suitable Java 1.8 found. In order to properly use the GAT Tools,
echo you need a suitable version of Java JDK(version no less than 1.8) installed on your system.
echo We recommend that you install the JDK version of JavaSE, available here:
echo   http://www.oracle.com/technetwork/java/javase/downloads
echo.
echo If you already have Java installed, you can define the JAVA_HOME environment
echo variable in Control Panel / System / Avanced System Settings to point to the
echo JDK folder.
echo.
echo.
@pause
goto :EOF
