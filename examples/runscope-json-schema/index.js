"use strict";

const axios = require('axios');
const log = require("./lib/helpers/logger");
const settings = require('./settings.js');
const jsonSchemaGenerator = require('json-schema-generator');

const apiUrl = "https://api.runscope.com";

//extract data from settings file
let {apikey,tests} = settings;

//add default authorization header to Runscope API calls
const authHeader = `Bearer ${apikey}`;
axios.defaults.headers.common['Authorization'] = authHeader;

//define functions to access Runscope API
function getRunscope(endpointUrl) {
	return axios.get(endpointUrl,);
}

function modifyRunscope(endpointUrl,postData) {
	return axios.put(endpointUrl,postData);
}

for (let z = 0; z < tests.length; z++) {
	let thisTest = tests[z];
	log.debug(thisTest);
	let {bucketKey,test_id,test_run_id} = thisTest;

	//set up variables for test data
	let stepDataArray = [];
	stepDataArray.push({"stepNumber": 0, "stepType": "initial"});

	//let test;
	let testResultUrl = `https://api.runscope.com/buckets/${bucketKey}/tests/${test_id}/results/${test_run_id}`;
	//log.debug(testResultUrl);

	let testDefinitionUrl = `https://api.runscope.com/buckets/${bucketKey}/tests/${test_id}/steps`;
	//log.debug(testDefinitionUrl);



	async function getTestInfo() {
		try {
			//get the definition of the test
			let thisTestDefinition = await getRunscope(testDefinitionUrl);
			let thisTestDefData = thisTestDefinition.data.data;
			
			//define step types
			for (let i=1; i<=thisTestDefData.length; i++) {
				stepDataArray.push({"stepNumber": i, "stepType": thisTestDefData[i-1].step_type })
			}

			//get the test result
			let thisTestResult = await getRunscope(testResultUrl);
			let resultData = thisTestResult.data;
			let stepArray = resultData.data.requests;

			//get step ids from test result
			let resultStepIds = stepArray.map(step => (step.uuid));

			//iterate through steps to get individual responses from steps and generate JSON schema
			for (let i=0; i < resultStepIds.length; i++) {
				const thisStepId = resultStepIds[i];
				const thisUrl = `${testResultUrl}/steps/${thisStepId}`
				const thisStepData = await getRunscope(thisUrl);
				const thisStepJson = JSON.parse(thisStepData.data.data.response.body);
				log.debug(`Step ${i}: ${JSON.stringify(thisStepJson)}`);
				

				let schemaObj;
				if (stepDataArray[i].stepType == "request") {
					schemaObj = jsonSchemaGenerator(thisStepJson);
					log.debug(JSON.stringify(schemaObj,undefined,4));
					stepDataArray[i].schema = schemaObj;
					//stepDataArray[i].schema.additionalProperties =  false;
				} else {
					stepDataArray[i].schema = null;
				}
				stepDataArray[i].json = thisStepJson;
				stepDataArray[i].uuid = resultStepIds[i];
			}

			//use JSON schema from above to add script to request steps to check JSON schema
			for (let i = 0; i < stepDataArray.length; i++) {
				//only need to modify request steps
				if (stepDataArray[i].stepType == "request"){
					let stepUrl = `${testDefinitionUrl}/${stepDataArray[i].uuid}`;
					log.debug(stepUrl);
					const thisStep = await getRunscope(stepUrl);
					let thisStepDefinition = thisStep.data.data;
					//remove properties that shouldn't be written back
					delete thisStepDefinition.request_id;
					delete thisStepDefinition.id;
					let thisSchema = stepDataArray[i].schema

					//add script to step
					let thisStepScript = `var thisSchema = ${JSON.stringify(thisSchema,undefined,4)};\n\nvar data = JSON.parse(response.body);\nassert.jsonSchema(data,thisSchema);`
					thisStepDefinition.scripts.push(thisStepScript);
					stepDataArray[i].definition = thisStepDefinition;
					
					try {
						const modifiedStep = await modifyRunscope(stepUrl,thisStepDefinition);
						log.debug(modifiedStep.status);
						log.debug(modifiedStep.data);
					} catch (e) {
						log.warn(e);
					}
				}

			}
			log.info(`Test updated: ${test_id}`);
			
		} catch (e) {
	    	log.warn(e);
	  	}
	}

	getTestInfo();

}

// function preventAdditionalProperties(jsonSchema) {
// 	let newObj = {};
// 	let newValue;
// 	const entries = Object.entries(jsonSchema)
// 	log.debug(entries);
// 	for (const [key, value] of entries) {
//  		log.debug(`Property: ${key} \nValue: ${value} Type ${typeof value}`)
//  		if(key == "properties") {
//  			jsonSchema.additionalProperties = false;
//  			//entries.push(["additionalProperties",false]);
//  		}
//  		if(typeof value == "object") {
//  			newValue = preventAdditionalProperties(value);
//  		} else {
//  			newValue = value;
//  		}
//  		jsonSchema[key]=newValue;		
// 	}
// 	newObj = jsonSchema;

// 	return newObj;

// }
