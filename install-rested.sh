#!/bin/sh
cd deps/CherryPy
python setup.py install
cd ../..
cd deps/docutils
python setup.py install
cd ../..
cd deps/Cheetah
python setup.py install
cd ../..
