openhrp-python: Python API and command line tools to control OpenHRP corba service

Install:

1. Install depending libraries
 $ sudo apt-get install git-core python-omniorb omniidl4-python python-progressbar

2. Clone from the repository
 $ git clone git://github.com/yosuke/openhrp-python.git openhrp-python

3. Run setup script
 $ cd openhrp-python
 $ sudo python setup.py install

Usage:

0. [Before using the script] Start OpenHRP corba services
 $ openhrp-model-loader
 $ openhrp-collision-detector
 $ openhrp-aist-dynamic-simulator

1. Load project file to dynamics simulator
 $ hrp --project ../OpenHRP-3.1.0-Release/sample/project/PA10Sample.xml 

2. Run dynamics simulation for 10 seconds (and save result to log file)
 $ hrp --run 10 --log sample.log

3. Load log file to view simulator
 $ hrp --project ../OpenHRP-3.1.0-Release/sample/project/PA10Sample.xml --view sample.log

Options:
  -h, --help            show this help message and exit
  -p FILE, --project=FILE
                        load project from FILE
  -r TIME, --run=TIME   run simulation for specified time period
  -l FILE, --log=FILE   save log to FILE
  -v FILE, --view=FILE  load log from FILE and send to viewer service
