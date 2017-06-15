# 2017-05-05
# Script to import a Runscope Environment
# Will read a JSON file that is Environment setting
# See https://www.runscope.com/docs/api/environments for 
# Runscope Documentation
# usage: python import_env.py <environmentname.json>
# For more on getting a Runscope Token, read here: 
# https://www.runscope.com/docs/api/authentication
# You can use the personal access token when you have
# created the application

import sys
import json
import requests
from runscope_config import *
from optparse import OptionParser
baseUrl = 'https://api.runscope.com'




def upload_env(file_name):
	if (options.testId):
		url = baseUrl + '/buckets/' + runscope_dest_bucket + '/tests/' + test_id + '/environments'
	else:
		url = baseUrl + '/buckets/' + runscope_dest_bucket + '/environments'
	if (options.uuid):
			url = url + "/" + dest_env_id
	with open(file_name,'r') as myfile:
		env_data = myfile.read()
		env_data =json.loads(env_data)

	headers = dict(Authorization='Bearer ' + runscope_token)
	
	if (options.modify):
		r = requests.put(url, headers=headers, json=env_data['data'])
	else:
		r = requests.post(url, headers=headers, json=env_data['data'])
	print r.status_code
	if r.status_code == 201:
		print 'Success - uploaded "' + env_data['data']['name'] + '" to bucket ' + runscope_dest_bucket
		if (options.testId):
			print 'Test: ' + test_id
		if (options.uuid):
			print 'Env ID:' + dest_env_id
	elif r.status_code == 200:
		print 'Success - Modified "' + env_data['data']['name'] + '" to bucket ' + runscope_dest_bucket
		if (options.testId):
			print 'Test: ' + test_id
		if (options.uuid):
			print 'Env ID:' + dest_env_id
	else:
		print 'Failure - ' + r.text


##------- Run the function above
parser = OptionParser()
parser.add_option("-b", "--bucket", dest="bucket", help="bucket key for env to import", metavar="BUCKET")
parser.add_option("-e", "--env", dest="uuid", help="env uuid for env to modify", metavar="ENV_UUID")
parser.add_option("-c", "--config", dest="configFile", help="name of config file", metavar="CONFIGFILE")
parser.add_option("-k", "--token", dest="runscopeToken", help="Runscope API Token", metavar="RUNSCOPETOKEN")
parser.add_option("-t", "--test", dest="testId", help="Runscope Test ID", metavar="TESTID")
parser.add_option("-v", "--verbose", action='store_true', dest="verbose",help="increase output verbosity")
parser.add_option("-m", "--modify", action='store_true', dest="modify",help="modify existing environment")
(options, args) = parser.parse_args()

if options.configFile:
	configFileName = options.configFile	
	mySettings = __import__(options.configFile)
else:
	mySettings = __import__("runscope_config")
runscope_dest_bucket = mySettings.runscope_dest_bucket
runscope_token = mySettings.runscope_token
if options.bucket:
	runscope_dest_bucket = options.bucket
if options.uuid:
	dest_env_id = options.uuid
if options.runscopeToken:
	runscope_token = options.runscopeToken
if options.testId:
	test_id = options.testId
inputfile = args[0]
if options.verbose:
	print "==================================================="
	print "ITEM          VALUE"
	print "------------- -------------------------------------"
	print "File:         " + inputfile
	print "Bucket:       " + runscope_dest_bucket
	if options.testId:
		print "Test ID:      " + test_id
	if options.uuid:
		print "Environment:  " + dest_env_id
	print "API Key:      " + runscope_token
	if options.modify:
		print "         Modify existing environment"
	print "==================================================="


upload_env(inputfile)

