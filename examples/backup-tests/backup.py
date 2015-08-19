import json
import time
import requests
import os
import sys
import inspect

# Global dictionary
g = {}

# Retrieves list of buckets for the authed account
# https://www.runscope.com/docs/api/buckets#bucket-list
def get_bucket_list():
    return _api_get_request( '/buckets', 200 )

# Retrieves test list for a given bucket key
# https://www.runscope.com/docs/api/tests#list
def get_bucket_test_list( bucket_key ):
    return _api_get_request( '/buckets/%s/tests' % bucket_key, 200 )

# Retrieves test details for a given test uuid in a bucket
# https://www.runscope.com/docs/api/tests#detail
def get_test_details( bucket_key,test_uuid ):
    return _api_get_request( '/buckets/%s/tests/%s' % (bucket_key,test_uuid), 200 )

# Execute HTTP request
def _api_get_request( path, status ):
    r = requests.get('%s/%s' % (g['base_url'],path), headers=g['headers'])
    if (r.status_code != status):
        _api_error_exit( r.status_code )
    return (json.loads(r.text))['data']

# Exits on API error, displaying status code and function
# name where error occurred.
def _api_error_exit( status_code ):
    sys.exit('API error - HTTP status code %s in %s' % (status_code,inspect.stack()[1][3]))


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

        # Fetch list of tests in this bucket
        bucket_test_list = get_bucket_test_list( b['key'] )

	# If bucket has tests, create directory
	if (len(bucket_test_list) > 0):
	    os.mkdir(b['path'])

	    # Loop through tests in bucket
	    for test in bucket_test_list:
		test_uuid = test["uuid"]
		test_name = test["name"]

                # Fetch details for this test and write to file
		test_json = get_test_details( b['key'], test_uuid )
		test_file = open('%s/%s.json' % (b['path'],test_uuid),'w')
		test_file.truncate()
		test_file.write(json.dumps(test_json))
		test_file.close()

if __name__ == "__main__": main()
