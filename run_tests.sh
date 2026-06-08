#!/bin/bash

# Zorg dat de root directory in het Python pad staat zodat modules gevonden worden
export PYTHONPATH=$PYTHONPATH:.

echo "--- Draaien van GameDotExe Unit Tests ---"

# Gebruik unittest discovery om alle tests in de tests/ map te vinden en te draaien
python3 -m unittest discover -s tests -p 'test_*.py'
exit $?