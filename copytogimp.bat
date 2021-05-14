@ECHO OFF

@REM Supply an argument for an alternative folder.
SET gimpversion=2.10
IF "%1" == "" (
    SET "gimpplugins=%UserProfile%\AppData\Roaming\GIMP\%gimpversion%\plug-ins\"
) ELSE (
    SET "gimpplugins=%1"
)
IF NOT EXIST "%gimpplugins%" (
    ECHO Version folder does not exist, probably wrong gimpversion & CMD /k & GOTO End
)

@REM This script folder, then src subfolder
SET "src=%~dp0src"
SET "name=cardassembler"
SET "pluginfolder=%gimpplugins%%name%"
SET "exclude=test_card_assembler.py my_mock.py"

IF NOT EXIST "%pluginfolder%" (
    MKDIR "%pluginfolder%" & ECHO Create a folder
)

Robocopy "%src%" "%pluginfolder%" *.py /xf %exclude%

@REM CMD /k
:End
