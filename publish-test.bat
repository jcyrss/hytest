del /S /Q  dist\*.gz
python setup.py bdist_wheel && twine upload dist/* --repository testpypi

pause