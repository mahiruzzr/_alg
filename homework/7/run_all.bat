@echo off
setlocal
if not exist build mkdir build

echo [build] diff_main.exe
g++ -std=c++17 -O2 -Wall -o build\diff_main.exe src\diff_main.cpp src\diff_dp.cpp src\diff_myers.cpp src\diff_types.cpp
if errorlevel 1 exit /b 1

echo [build] cnk.exe
g++ -std=c++17 -O2 -Wall -o build\cnk.exe src\cnk.cpp
if errorlevel 1 exit /b 1

echo.
echo ============ self test ============
build\diff_main.exe selftest
if errorlevel 1 exit /b 1

echo.
echo ============ diff demo ============
build\diff_main.exe demo

echo.
echo ============ diff benchmark (similar files) ============
build\diff_main.exe bench 2000 40
build\diff_main.exe bench 5000 100

echo.
echo ============ diff benchmark (dissimilar files) ============
build\diff_main.exe bench 1000 1000
build\diff_main.exe bench 2000 2000

echo.
echo ============ C(n,k) ============
build\cnk.exe show

echo.
echo ============ independent verification ============
python verify.py
