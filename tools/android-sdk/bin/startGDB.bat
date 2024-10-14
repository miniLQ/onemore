@echo off
cd ..\python\bin\
set PYTHONHOME=%1
set PYTHONPATH=%2
set path=%path%;%2;
set parameter=%3
SHIFT
set parameter=%parameter% %3
SHIFT
set parameter=%parameter% %3
SHIFT
set parameter=%parameter% %3
SHIFT
set parameter=%parameter% %3
SHIFT
set parameter=%parameter% %3
SHIFT
set parameter=%parameter% %3
SHIFT
set parameter=%parameter% %3
SHIFT
set parameter=%parameter% %3
SHIFT
set parameter=%parameter% %3
SHIFT
set parameter=%parameter% %3
SHIFT
set parameter=%parameter% %3
SHIFT
set parameter=%parameter% %3
SHIFT
set parameter=%parameter% %3
SHIFT
set parameter=%parameter% %3
SHIFT
set parameter=%parameter% %3
gdb.exe -iex "set osabi GNU/Linux" %parameter%
exit
