Creating Runscope Tests with API
============
A collection of tests in JSON that you can instantly
import into your Runscope account via the API. Also
included is a sample app that will make the POST
API call.

This serves as an example of how easy it is to create
tests programmatically with the Runscope API.

Requirements
------------
- Python
- Python Requests library
- Runscope API key (access token)

Configuration
------------
Copy ```config.json.sample``` to ```config.json``` and then 
make the necessary modifications (add your access token
from Runscope).

Obtaining an Access Token
------------
To create an access token, login to your Runscope account and navigate to [https://www.runscope.com/applications](https://www.runscope.com/applications). Here, click ```Create Application``` -- for name, type in *Test Backup App*. For website and callback URLs, you can just type in ```https://www.runscope.com``` as placeholders (these URLs are never used -- we're just creating an application for the personal access token). After you've created the application, copy the personal access token (i.e. ```5ffffffe-ab99-43ff-7777-3333deee99f9```) and use it in ```config.json```.

Running the App
------------
$ python create_test.py tests/deck_of_cards_api_test.json
$ python create_test.py tests/minimal_test.json

ChangeLog
------------
2015-08-18 - Initial release.
