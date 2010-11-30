openhrp-python: Python API and command line tools to control OpenHRP corba service

Example usage:

1. Load project file to dynamics simulator
$ python OpenHRPSimulation.py --project ../OpenHRP-3.1.0-Release/sample/project/PA10Sample.xml 

2. Run synamics simulation for 10 seconds (and save result to log file)
$ python OpenHRPSimulation.py --run 10 --log sample.log

3. Load log file to view simulator
$ python OpenHRPSimulation.py --project ../OpenHRP-3.1.0-Release/sample/project/PA10Sample.xml --view sample.log


