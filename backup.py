import json
import time
import requests
import os

with open('config.json') as config_file:
    config = json.load(config_file)

runscope_headers = {'Authorization':'Bearer '+config["runscope"]["access_token"]}

today = time.strftime('%Y-%m-%dT%H:%M')

workdir = os.getcwd()

r = requests.get("https://api.runscope.com/buckets",headers=runscope_headers)
buckets_json = json.loads(r.text)
for bucket in buckets_json["data"]:
    bucket_name = bucket["name"]
    print "In " + bucket_name
    bucket_key = bucket["key"]
    bucket_path = "%s/%s_%s" % (workdir,today,bucket_key)
    os.mkdir(bucket_path)
    os.chdir(bucket_path)
    r = requests.get("https://api.runscope.com/buckets/"+bucket_key+"/tests",headers=runscope_headers)
    tests_json = json.loads(r.text)
    for test in tests_json["data"]:
        test_uuid = test["uuid"]
	test_name = test["name"]
	print "    " + test_name

        r = requests.get("https://api.runscope.com/buckets/"+bucket_key+"/tests/"+test_uuid,headers=runscope_headers)
	test_json = json.loads(r.text)
	test_file = open(test_uuid + '.json','w')
	test_file.truncate()
	test_file.write(json.dumps(test_json["data"]))
	test_file.close()
