del /S /Q  dist\*.*
python setup.py bdist_wheel && twine upload dist/*

pause