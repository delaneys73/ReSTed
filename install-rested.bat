@ECHO OFF
cd deps\CherryPy
c:\python27\python.exe setup.py install
cd deps\docutils
c:\python27\python.exe setup.py install
cd deps\Cheetah
c:\python27\python.exe setup.py install