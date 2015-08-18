import json
import time
import requests
import os
import sys

# Global dictionary
g = {}

# Retrieves list of buckets for the authed account
def get_bucket_list():
    url = "%s/buckets" % g['base_url']
    r = requests.get(url, headers=g['headers'])
    buckets_json = json.loads(r.text)
    return buckets_json['data']

# Retrieves test list for a given bucket key
def get_bucket_test_list( bucket_key ):
    url = "%s/buckets/%s/tests" % (g['base_url'],bucket_key)
    r = requests.get(url,headers=g['headers'])
    tests_json = json.loads(r.text)
    return tests_json['data']

# Retrieves test details for a given test uuid in a bucket
def get_test_details( bucket_key,test_uuid ):
    r = requests.get("%s/buckets/%s/tests/%s" % (g['base_url'],bucket_key,test_uuid), headers=g['headers'])
    test_json = json.loads(r.text)
    return test_json['data']

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
