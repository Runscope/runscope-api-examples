import inspect
import json
import os
import sys
import time

import requests

# Global configuration
runscopeApiConfig = {
    'base_url': 'https://api.runscope.com'
}


def get_bucket_list():
    """
        Retrieves list of buckets for the authed account
        https://www.runscope.com/docs/api/buckets#bucket-list
    """
    return _api_get_request('/buckets', 200)


def get_bucket_test_list(bucket_key):
    """
        Retrieves test list for a given bucket key
        https://www.runscope.com/docs/api/tests#list
    """
    return _api_get_request('/buckets/%s/tests' % bucket_key, 200)


def get_test_details(bucket_key, test_id):
    """
        Retrieves test details for a given test id in a bucket
        https://www.runscope.com/docs/api/tests#detail
    """
    return _api_get_request('/buckets/%s/tests/%s' % (bucket_key, test_id), 200)


def _api_get_request(path, status):
    """Execute HTTP request"""
    r = requests.get('%s/%s' % (runscopeApiConfig['base_url'], path), headers=runscopeApiConfig['headers'])
    if r.status_code != status:
        _api_error_exit(r.status_code)
    return (json.loads(r.text))['data']


def _api_error_exit(status_code):
    """
        Exits on API error, displaying status code and function
        name where error occurred.
    """
    sys.exit('API error - HTTP status code %s in %s' % (status_code, inspect.stack()[1][3]))


def main():
    with open('config.json') as config_file:
        config = json.load(config_file)

    runscopeApiConfig['headers'] = {'Authorization': 'Bearer %s' % config["runscope"]["access_token"]}

    # Timestamp used for directory name
    today = time.strftime('%Y-%m-%dT%H:%M')

    # Set current directory as working directory where
    # the backups will be saved
    workdir = os.getcwd()

    # Fetch list of buckets for authed account
    bucket_list = get_bucket_list()

    # Loop through bucket list
    for bucket in bucket_list:
        file_name = ("%s_%s" % (today, bucket['key'])).replace(':', '___')
        b = {
            'name': bucket['name'],
            'key': bucket['key'],
            'path': (os.path.join(workdir, file_name))
        }

        # Fetch list of tests in this bucket
        bucket_test_list = get_bucket_test_list(b['key'])

        # If bucket has tests, create directory
        if len(bucket_test_list) > 0:
            os.mkdir(b['path'])

            # Loop through tests in bucket
            for test in bucket_test_list:
                test_id = test["id"]
                test_name = test["name"]

                # Fetch details for this test and write to file
                test_json = get_test_details(b['key'], test_id)
                test_file = open('%s/%s.json' % (b['path'], test_id), 'w')
                test_file.truncate()
                test_file.write(json.dumps(test_json))
                test_file.close()


if __name__ == "__main__":
    main()
