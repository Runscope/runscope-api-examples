# 2017-05-05
# Script to export a Runscope Environment
# Will write to a file JSON configuration of an Environment
# See https://www.runscope.com/docs/api/environments for 
# Runscope Documentation
# usage: python runscope_export_env.py
# will export a file with name of the environment to current directory
# For more on getting a Runscope Token, read here: 
# https://www.runscope.com/docs/api/authentication
# You can use the personal access token when you have
# created the application

import requests
import importlib
import json
from optparse import OptionParser

def export_env(m_bucket_key, m_env_id, m_runscope_token, m_test_id=False):
	if (m_test_id):
		url = 'https://api.runscope.com/buckets/' + m_bucket_key + '/tests/' + m_test_id + '/environments/' + m_env_id
		print "exporting test"
	else:
		url = 'https://api.runscope.com/buckets/' + m_bucket_key + '/environments/' + m_env_id
		print "exporting shared"
	headers = dict(Authorization='Bearer ' + m_runscope_token)
	r = requests.get(url, headers=headers)
	if r.status_code == 200:
		env_name = r.json()["data"]["name"]
		g = open(env_name + '.json', 'w')
		g.write(r.text)
		print "Successfully exported '" + env_name + ".json'"
	else:
		print 'Failure - ' + r.text

##------- Run the function above
test_id = False
parser = OptionParser()
parser.add_option("-b", "--bucket", dest="bucket", help="bucket key for env to export", metavar="BUCKET")
parser.add_option("-e", "--env", dest="uuid", help="env uuid for env to export", metavar="ENV_UUID")
parser.add_option("-c", "--config", dest="configFile", help="name of config file", metavar="CONFIGFILE")
parser.add_option("-k", "--token", dest="runscopeToken", help="Runscope API Token", metavar="RUNSCOPETOKEN")
parser.add_option("-t", "--test", dest="testId", help="Runscope Test ID", metavar="TESTID")
parser.add_option("-v", action='store_true', dest="verbose",help="increase output verbosity")
(options, args) = parser.parse_args()
if options.configFile:
	configFileName = options.configFile	
	mySettings = __import__(options.configFile)
else:
	mySettings = __import__("runscope_config")
master_bucket_key = mySettings.master_bucket_key
master_env_id = mySettings.master_env_id
runscope_token = mySettings.runscope_token
if options.bucket:
	master_bucket_key = options.bucket
if options.uuid:
	master_env_id = options.uuid
if options.runscopeToken:
	runscope_token = options.runscopeToken
if options.testId:
	test_id = options.testId
if options.verbose:
	print "==================================================="
	print "ITEM          VALUE"
	print "------------- -------------------------------------"
	print "Bucket:       " + master_bucket_key
	if options.testId:
		print "Test ID:      " + test_id
	print "Environment:  " + master_env_id
	print "API Key:      " + runscope_token
	print "==================================================="
export_env(master_bucket_key, master_env_id, runscope_token, test_id)
