import requests  # make sure this is installed
#from jsonschema import validate
#from jsonschema.exceptions import ValidationError

from uuid import UUID
import uuid
import json
import time
import requests
import os
import sys
import inspect
import re


# Global dictionary
g = {}

class PostmanCollection:
    def __init__(self, colname):
        self.name = colname
        self.requests = []
        self.folders = []
        self.id = str(uuid.uuid4())
        self.name = ""
        self.timestamp = 0
        self.owner = 0
        self.hasRequests = True
        self.order = []

    def addRequest(self, req):
        self.requests.append(req)
        req.collectionId = str(self.id)
        #self.order.append(req.id)
        return id

    def addFolder(self, folder):
        self.folders.append(folder)
        return id


class PostmanFolder:
    def __init__(self, name):
        self.name = name
        self.id = str(uuid.uuid4())
        self.description = ""
        self.collection_name = ""
        self.collection_id = 0
        self.orderlist = []

    def addRequestOrder(self, reqId):
        self.orderlist.append(reqId)
        return self.id

class PostmanRequest:
    def __init__(self, name):
        self.name = name
        self.id = str(uuid.uuid4())
        self.headers = ""
        self.url = ""
        self.pathvariables = {}
        self.preRequestScript = ""
        self.method = "POST"
        self.data = [{}]
        self.rawModeData=""

        self.datamode = "params"
        self.descriptionFormat = "html"
        self.description=""
        self.time = 1440620734887
        self.version = 2

        self.responses = []
        self.tests = ""
        self.collectionId = "3838b6df-9d49-bdad-f99b-d6c83e9b83b1"
        self.name = ""
        self.folder = ""

class PostmanCollectionEncoder(json.JSONEncoder):
    def default(self, obj):

        if isinstance(obj, UUID):
            return str(obj)
        elif isinstance(obj, PostmanCollection):
            collections = { }
            collections.update({"id":str(obj.id)})
            collections.update({"name":obj.name})
            collections.update({"order":obj.order})
            foldersCol = []

            requestsCol=[]
            aFolder = PostmanFolder("test")
            for aFolder in obj.folders:
                folderCol={}
                folderCol.update({"id": aFolder.id})
                folderCol.update({"name": aFolder.name})
                folderCol.update({"order":aFolder.orderlist})
                folderCol.update({"description":aFolder.description})
                folderCol.update({"collection_name":aFolder.collection_name})
                folderCol.update({"collection_id":aFolder.collection_id})
                folderCol.update({"collection":aFolder.collection_id})
                foldersCol.append(folderCol)
            collections.update({"folders":foldersCol})

            for aRequest in obj.requests:
                requestCol={}
                requestCol.update({"id":aRequest.id})
                requestCol.update({"headers":aRequest.headers})
                requestCol.update({"url":aRequest.url})
                requestCol.update({"pathVariables":{}})
                requestCol.update({"preRequestScript":""})
                requestCol.update({"method":aRequest.method})
                requestCol.update({"data":aRequest.data})
                requestCol.update({"dataMode":aRequest.datamode})
                requestCol.update({"descriptionFormat":"html"})
                requestCol.update({"timestamp":time.time()})
                requestCol.update({"version":2})
                requestCol.update({"responses":[]})
                requestCol.update({"tests":""})
                requestCol.update({"collectionId":aRequest.collectionId})
                requestCol.update({"name":aRequest.name})
                requestCol.update({"description":aRequest.description})
                requestCol.update({"folder":aRequest.folder})
                requestCol.update({"rawModeData":aRequest.rawModeData})

                requestsCol.append(requestCol)
            collections.update({"requests":requestsCol})
            #collectionsString = json.dumps(collections,indent=2)
            return collections
        else:
            collectionString = "{ }"
            return collectionString
        return json.JSONEncoder.default(self, obj)

# Add Postman collection
def add_postman_collection(postmanScript, id, name, order, folders, ):
    postmanScript += json.dumps("{ ")


# Retrieves list of buckets for the authed account
# https://www.runscope.com/docs/api/buckets#bucket-list
def get_bucket_list():
    return _api_get_request('/buckets', 200)


# Retrieves test list for a given bucket key
# https://www.runscope.com/docs/api/tests#list
def get_bucket_test_list(bucket_key):
    return _api_get_request('/buckets/%s/tests?count=70' % bucket_key, 200)


# Retrieves test details for a given test id in a bucket
# https://www.runscope.com/docs/api/tests#detail
def get_test_details(bucket_key, test_id):
    Testdata = _api_get_request('/buckets/%s/tests/%s' % (bucket_key, test_id), 200)
    return Testdata


# Retrieves test step details for a given test id in a bucket, test stepid
# https://www.runscope.com/docs/api/tests#detail
def get_test_step_details(bucket_key, test_id, step_id):
    testData = _api_get_request('/buckets/%s/tests/%s/steps/%s' % (bucket_key, test_id, step_id), 200)
    return testData


# Retrieves shared test environment  details for a given bucket
def get_shared_test_env(bucket_key):
    return _api_get_request('/buckets/%s/environments' % (bucket_key), 200)


# Retrieves test results for a given test id in a bucket
# https://www.runscope.com/docs/api/results#test-run-detail
def get_test_run_details(bucket_key, test_id):
    return _api_get_request('/buckets/%s/tests/%s/results/latest' % (bucket_key, test_id), 200)


# clean up file name using test case name
def cleanFileName(file_name):
    # replace all non word chars
    file_name = re.sub(r"[^\w\s]", '', file_name)
    # replae spaces with one '_'
    file_name = re.sub(r"\s+", '_', file_name)
    return file_name


# Execute HTTP request
def _api_get_request(path, status):
    r = requests.get('%s/%s' % (g['base_url'], path), headers=g['headers'])
    if r.status_code != status:
        _api_error_exit(path, r.status_code)
    return (json.loads(r.text))['data']


# Exits on API error, displaying status code and function
# name where error occurred.
def _api_error_exit(path, status_code):
    sys.exit('API path %s - API error - HTTP status code %s in %s' % (path, status_code, inspect.stack()[1][3]))


# print text after replacing variables defined in config.json and cleaning up
def replaceVariables(varlist, text):
    for key, value in varlist.iteritems():
        varname = "{{" + key + "}}"
        text = re.sub(varname, value, text)
        text = re.sub("\\r\\n", '', text)
    return text


def main():
    with open('config.json') as config_file:
        config = json.load(config_file)

    g['headers'] = {'Authorization': 'Bearer %s' % config["runscope"]["access_token"]}
    g['base_url'] = 'https://api.runscope.com'

    # Timestamp used for directory name
    today = time.strftime('%Y-%m-%dT%H:%M')

    # Set current directory as working directory where
    # the backups will be saved
    workdir = os.getcwd()
    # Fetch list of buckets for authed account
    bucket_list = get_bucket_list()

    # Loop through bucket list
    for bucket in bucket_list:
        b = dict()
        b['name'] = bucket['name']
        b['key'] = bucket['key']
        b['path'] = "%s/%s_%s" % (workdir, today, b['key'])
        # Below condition is to test with smaller bucket of test cases
        if b['key'] == '80e4gnwm9xxi':
            # Fetch list of tests in this bucket
            print "----" + bucket['name'] + "----"
            bucket_test_list = get_bucket_test_list(b['key'])

            # future change - retrieve environment variables and insert them where they are used in testcases
            # shared_test_env = get_shared_test_env(b['key'])
            # print shared_test_env[0]['initial_variables']
            # If bucket has tests
            if len(bucket_test_list) > 0:
                test_file = open('%s.json' % (cleanFileName(b['name'])), 'w')
                test_file.truncate()
                collection = PostmanCollection(b['name'])
                collection.name = b['name']
                # Loop through tests in bucket
                for test in bucket_test_list:
                    test_id = test["id"]
                    test_name = test["name"]
                    print test_name
                    print "___________________"
                    print
                    folder = PostmanFolder(test_name)
                    folder.description = test['description']

                    # Fetch details for this test and write to file
                    test_steps = get_test_details(b['key'], test_id)

                    # no need to get test run details for this script
                    # test_results = get_test_run_details(b['key'],test_id)

                    steps = test_steps['steps']
                    # test_file = open('%s.txt' % (cleanFileName(test_name)),'w')
                    # test_fle.truncate()

                    for testStep in steps:
                        # don't need to retrieve test step details as test details has all needed info
                        # stepDetail = get_test_step_details(b['key'],test_id,testStep['id'])

                        Request = PostmanRequest("test")
                        if 'description' in testStep:
                            Request.description = testStep['']
                        if 'descriptionFormat' in testStep:
                            Request.descriptionFormat = testStep['descriptionFormat']

                        textBuffer = "\n\n"
                        if 'note' in testStep:
                            if testStep['note'] is not None:
                                textBuffer += "# " + testStep['note'] + "\n"
                                Request.name = testStep['note']

                        if 'method' in testStep:
                            Request.method = testStep['method']

                        if 'headers' in testStep:
                            textBuffer += ""
                            for key, value in testStep['headers'].iteritems():
                                textBuffer += key + ":" + replaceVariables(config["runscope"], value[0]) + "\n"

                        Request.headers = textBuffer

                        formdata = ""
                        if 'form' in testStep:
                            dataForm = []
                            for key1, value1 in testStep['form'].iteritems():
                                dataForm.append({"key": replaceVariables(config["runscope"], key1),
                                                 "value": replaceVariables(config["runscope"], str(value1)),
                                                 "type": "text",
                                                 "enabled": True})
                            Request.datamode = "params"
                            Request.data = dataForm

                        if 'body' in testStep and testStep['body'] != "":
                            formdata = testStep['body']
                            # replaceVariables(config["runscope"],testStep['body'])
                            textBuffer = replaceVariables(config["runscope"], formdata)
                            Request.datamode = "raw"
                            if textBuffer != '':
                                Request.rawModeData = textBuffer

                        textBuffer = ""
                        if 'url' in testStep:
                            textBuffer += " " + replaceVariables(config["runscope"], testStep['url']) + "\n"
                        Request.url = textBuffer
                        Request.folder = folder.addRequestOrder(Request.id)
                        collection.addRequest(Request)
                        # test_file.write(json.dumps(Request))
                    folder.collection_id = collection.addFolder(folder)
                    #collection.addFolder(folder)
                json.dump(collection,fp=test_file,cls=PostmanCollectionEncoder,indent=2)
                test_file.close()


if __name__ == "__main__": main()

