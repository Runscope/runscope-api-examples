import json
import time
import requests
import os
import sys
import inspect
import re

# Global dictionary
g = {}

# Retrieves list of buckets for the authed account
# https://www.runscope.com/docs/api/buckets#bucket-list
def get_bucket_list():
    return _api_get_request( '/buckets', 200 )

# Retrieves test list for a given bucket key
# https://www.runscope.com/docs/api/tests#list
def get_bucket_test_list( bucket_key ):
    return _api_get_request( '/buckets/%s/tests?count=70' % bucket_key, 200 )

# Retrieves test details for a given test id in a bucket
# https://www.runscope.com/docs/api/tests#detail
def get_test_details( bucket_key,test_id ):
    Testdata=_api_get_request( '/buckets/%s/tests/%s' % (bucket_key,test_id), 200 )
    return Testdata

# Retrieves test step details for a given test id in a bucket, test stepid
# https://www.runscope.com/docs/api/tests#detail
def get_test_step_details( bucket_key,test_id, step_id ):
    testData=_api_get_request( '/buckets/%s/tests/%s/steps/%s' % (bucket_key,test_id,step_id), 200 )
    return testData

# Retrieves shared test environment  details for a given bucket
def get_shared_test_env( bucket_key ):
    return _api_get_request( '/buckets/%s/environments' % (bucket_key), 200 )

# Retrieves test results for a given test id in a bucket
#https://www.runscope.com/docs/api/results#test-run-detail
def get_test_run_details( bucket_key,test_id ):
    return _api_get_request( '/buckets/%s/tests/%s/results/latest' % (bucket_key,test_id), 200 )

# clean up file name using test case name
def cleanFileName( file_name):
    #replace all non word chars
    file_name = re.sub(r"[^\w\s]",'',file_name)
    # replae spaces with one '_'
    file_name = re.sub(r"\s+",'_',file_name)
    return file_name

# Execute HTTP request
def _api_get_request( path, status ):
    r = requests.get('%s/%s' % (g['base_url'],path), headers=g['headers'])
    if (r.status_code != status):
        _api_error_exit(path, r.status_code )
    return (json.loads(r.text))['data']

# Exits on API error, displaying status code and function
# name where error occurred.
def _api_error_exit( path, status_code ):
    sys.exit('API path %s - API error - HTTP status code %s in %s' % (path, status_code,inspect.stack()[1][3]))


# print text after replacing variables defined in config.json and cleaning up
def replaceVariables(varlist,text):
  for key, value in varlist.iteritems():
      varname = "{{" + key + "}}"
      text = re.sub(varname, value,text)
      text = re.sub("\\r\\n",'',text)
  return text

def main():
    with open('config.json') as config_file:
        config = json.load(config_file)

    g['headers'] = {'Authorization':'Bearer %s' % config["runscope"]["access_token"]}
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
        b = {}
        b['name'] = bucket['name']
        b['key'] = bucket['key']
        b['path'] = "%s/%s_%s" % ( workdir, today,b['key'] )
        # Below confition is to test with smaller bucket of test cases
        if (b['key'] != ' '):
          # Fetch list of tests in this bucket
          print "----" + bucket['name'] + "----"
          bucket_test_list = get_bucket_test_list( b['key'] )

          #future change - retrieve environment variables and insert them where they are used in testcases
          #shared_test_env = get_shared_test_env(b['key'])
          #print shared_test_env[0]['initial_variables']

        # If bucket has tests
          if (len(bucket_test_list) > 0):

            # Loop through tests in bucket
            for test in bucket_test_list:
                test_id = test["id"]
                test_name = test["name"]
                print test_name
                print "___________________"
                print
                # Fetch details for this test and write to file
                test_steps = get_test_details( b['key'], test_id )

                # no need to get test run details for this script
                #test_results = get_test_run_details(b['key'],test_id)

                steps = test_steps['steps']
                test_file = open('%s.txt' % (cleanFileName(test_name)),'w')
                test_file.truncate()
                for testStep in steps:
                  # don't need to retrieve test step details as test details has all needed info
                  #stepDetail = get_test_step_details(b['key'],test_id,testStep['id'])

                  textBuffer ="\n\n"
                  if 'note' in testStep:
                    if testStep['note'] is not None:
                        textBuffer += "# " + testStep['note'] + "\n"

                  #if your test site uses 3rd party cert you don't need --insecure flag
                  textBuffer += "curl --insecure -X"
                  if 'method' in testStep:
                    textBuffer +=  testStep['method']+" "

                  if 'headers' in testStep:
                    for key,value in testStep['headers'].iteritems():
                      textBuffer +=  " -H" + "'"+key+":"+ replaceVariables(config["runscope"], value[0]) + "' "

                  formdata =""
                  if 'form' in testStep:
                    for key1,value1 in testStep['form'].iteritems():
                        formdata += key1+"="+value1[0] + '&'
                  if 'body' in testStep:
                    textBuffer += " -d " + "'" + testStep['body']
                    #replaceVariables(config["runscope"],testStep['body'])
                    textBuffer += replaceVariables( config["runscope"], formdata) + "'"
                  if 'url' in testStep:
                    textBuffer += " " + replaceVariables(config["runscope"],testStep['url'] ) + "\n"
                  test_file.write(textBuffer)
            test_file.close()




if __name__ == "__main__": main()
