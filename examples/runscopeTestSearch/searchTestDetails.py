import requests
import importlib
import json
from optparse import OptionParser

searchPhrase = "YourSearchPhrase"
runscope_token = "YOUR_TOKEN_HERE"


def search_tests(m_runscope_token, m_search_phrase):
	url = 'https://api.runscope.com/buckets'
	headers = dict(Authorization='Bearer ' + m_runscope_token)
	
	#get list of buckets
	r = requests.get(url, headers=headers)
	theSearchPhrase = m_search_phrase
	testList = [];
	if r.status_code == 200:
		myBuckets = r.json()["data"]
				
		#loop through buckets to get tests from each bucket
		for bucket in myBuckets:
			thisBucket =  bucket["key"]
			url2 = url + "/" + thisBucket +"/tests"
			url2full = url2 + "?count=200"
			r2 = requests.get(url2full, headers=headers)
			if r2.status_code == 200:
				myTests = r2.json()["data"]
			
				#loop through test to get test Details for each test in this bucket
				for test in myTests:
					thisTestId = test["id"]
					url3 = url2 + "/" + thisTestId
					r3 = requests.get(url3, headers=headers)
					if r3.status_code == 200:
						myTestSteps = r3.json()["data"]["steps"]
						for thisTestStep in myTestSteps:
							print "Searching: " + url3
							if thisTestStep.has_key("url"):
								thisUrl = thisTestStep["url"]
								thisUrl = thisTestStep["url"]
								if thisUrl.find(theSearchPhrase) >= 0:
									print url3
									print thisUrl
									print "YOU FOUND A MATCH"
									thisTestUrl = "https://www.runscope.com/radar/" + thisBucket + "/" + thisTestId + "/overview"
									testList.append(thisTestUrl)
							print "=================="
					else:
						print 'Failure - failed to get test: ' + url3  #+ r.text				
						print "=================="
					



			else:
				print 'Failure - failed to get test: ' + thisBucket #+ r.text				

	else:
		print 'Failure - failed to get bucket list' #+ r.text

	print "******************"
	print "Tests found with search phrase: " + theSearchPhrase
	for foundTest in testList:
		print foundTest


##------- Run the function above
parser = OptionParser()
parser.add_option("-s", "--search", dest="searchPhrase", help="phrase to search for", metavar="SEARCHPHRASE")
parser.add_option("-k", "--token", dest="runscopeToken", help="Runscope API Token", metavar="RUNSCOPETOKEN")
(options, args) = parser.parse_args()

if options.runscopeToken:
	runscope_token = options.runscopeToken

if options.searchPhrase:
	searchPhrase = options.searchPhrase

search_tests(runscope_token,searchPhrase)
