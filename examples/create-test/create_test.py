import json
import requests
import sys
import inspect

# Global dictionary
g = {}

# Retrieve name from account resource
def get_account_info():
    j = _api_get_request( "/account", 200 )
    g["name"] = j["name"]
    print "\nHello %s.\n" % g["name"]

# Retrieves list of buckets for the authed account
def get_bucket_list():
    return _api_get_request( "/buckets", 200 )

# Bucket selection (user input from terminal)
def select_bucket():
    get_account_info()
    buckets = get_bucket_list()

    for x in range(0,len(buckets)):
        print "%s - %s (%s)" % ( x, buckets[x]["name"], buckets[x]["key"] )

    selection = -1
    while (selection < 0 or selection > len(buckets)-1):
        selection = input ("\nSelect destination bucket for the new test: ")

    g["bucket_key"] = buckets[selection]["key"]

# Read and validate test from JSON file
def read_test():
    try:
        # Open and read the file
        f = open(sys.argv[1], "r")
	t = f.read()
        j = json.loads(t)

	# Trigger a KeyError exception if a test name doesn"t exist
	j["name"] = j["name"]

    except IOError as e:
        sys.exit("\nI/O error({0}): {1}\n".format(e.errno, e.strerror))
    except ValueError:
        sys.exit("\nInvalid JSON in file %s\n" % sys.argv[1])
    except KeyError:
        sys.exit("\nInvalid test definition JSON in file %s: Test name is required.\n" % sys.argv[1])

    g["new_test"] = json.dumps(j)

# Create test with API
def create_test():
    data = _api_post( "/buckets/%s/tests" % g["bucket_key"], g["new_test"], 201)
    print "\nNew test created.\n"

# Execute HTTP GET request
def _api_get_request( path, status ):
    r = requests.get("%s/%s" % (g["base_url"],path), headers=g["headers"])
    if (r.status_code != status):
        _api_error_exit( r.status_code )
    return (json.loads(r.text))["data"]

# Execute HTTP POST request
def _api_post( path, data, status ):
    r = requests.post("%s/%s" % (g["base_url"],path), data=data, headers=g["headers"])
    if (r.status_code != status):
        _api_error_exit( r.status_code )
    return (json.loads(r.text))["data"]

# Exits on API error, displaying status code and function
# name where error occurred.
def _api_error_exit( status_code ):
    sys.exit("API error - HTTP status code %s in %s" % (status_code,inspect.stack()[1][3]))

def main():
    with open("config.json") as config_file:
	config = json.load(config_file)

    g["headers"] = {"Authorization":"Bearer %s" % config["runscope"]["access_token"],"Content-type":"application/json"}
    g["base_url"] = "https://api.runscope.com"

    read_test()
    select_bucket()
    create_test()
    sys.exit()

if __name__ == "__main__": main()
