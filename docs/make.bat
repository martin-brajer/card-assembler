@ECHO OFF
pushd %~dp0

@REM set SPHINXBUILD=sphinx-build
@REM set SOURCEDIR=source
@REM set BUILDDIR=build/html
@REM %SPHINXBUILD% -b html -d build/doctrees %SOURCEDIR% %BUILDDIR%


sphinx-build -b html -d build/doctrees source build/html
popd

cmd /k