@ECHO OFF
PUSHD %~dp0

SET SPHINXBUILD=sphinx-build
SET BUILDER=html
SET BUILDPATH=build/doctrees
SET SOURCEDIR=source
SET OUTPUTDIR=build/html

%SPHINXBUILD% -b %BUILDER% -d %BUILDPATH% %SOURCEDIR% %OUTPUTDIR%
@REM sphinx-build -b html -d build/doctrees source build/html

POPD
CMD /k