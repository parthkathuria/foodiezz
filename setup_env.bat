:: Batch script to setup the environment for the App and install all the required dependencies
:: You only need to run this script once.
:: Requires Python3.6 or higher installed in the system

py -m pip install virtualenv
py -m venv venv
.\venv\Scripts\activate & pip install -r requirements.txt
