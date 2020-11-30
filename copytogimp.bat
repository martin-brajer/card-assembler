@ECHO OFF

@REM Supply an argument for an alternative folder.
IF "%1" == "" (
    set gimpplugins="C:\Users\Villentretenmerth\AppData\Roaming\GIMP\2.10\plug-ins\"
) ELSE (
    set gimpplugins=%1
)

@REM This script folder, then src subfolder
set src=%~dp0\src\
set name=cardassembler
set pluginfolder=%gimpplugins%%name%

IF NOT EXIST %pluginfolder% MKDIR %pluginfolder%

copy %src% %pluginfolder%
@REM copy %src%cardassembler.py %pluginfolder%
@REM copy %src%blueprint.py %pluginfolder%

@REM cmd /k