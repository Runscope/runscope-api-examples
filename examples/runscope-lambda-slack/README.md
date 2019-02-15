Custom Slack notifications for Runscope
=====================

This utility is an node.js AWS Lambda function to be used in conjunction with Runscope for custom Slack notifications. As written, this function will send a custom notification (with a friendly name different than the test name and/or a custom message as part of the notificaiton) to Slack and has the option to send a notification to a different channel if the test fails because the Runscope Agent is disconnected. This ensures that the team responsible for the API is notified if the API being tested fails, whereas the team responsible for maintaining the Runscope agent is notified if the agent is down. **WARNING: IF YOU USE THIS PROXY AS CONFIGURED, THE API TEAM WILL NOT BE NOTIFIED THAT THEIR API WAS NOT TESTED**

## Installation
If Node.js is not installed, install it from https://nodejs.org/. Once complete, check by running ```node -v``` from a terminal window to show the install version.

Clone the repo:
`git clone https://github.com/samaybar/runscope-lambda-slack.git`
`cd runscope-lambda-slack`

Install node module dependencies:
`npm install`

## How to Use

### Create a AWS Lambda Function
(This assumes you have some familiarity with AWS Lambda)

- Compress the files in the directory into a .zip file (zip file provided for version as written)
- From the AWS Lambda console, create a new function
- Upload the compressed .zip file
- Add an **API Gateway** as a trigger. I recommend configuring as **Open with API key** but you can also choose **Open**  
- Copy the **API endpoint** and the **API key** to use in Runscope

### Configure the Slack integrations in Slack
- Follow the instructions at https://www.runscope.com/docs/api-testing/slack/ to integrate Slack with Runscope; however stop when you have generated the Webhook URL in Slack
- Generate the Slack Webhook URL for both the main channel and (optionally) the agent failure channel

### Configure the Advanced Webhook in Runscope

- From the top right Runscope icon choose **Connected Services**
- Under **webhooks** choose **Connect*
- Set your threshold as desired
- For the **URL** use the **API endpoint** you copied above
- Be sure to add the following headers:
```bash
Content-Type: application/json
x-api-key: [API key]
slackurl: [Slack Webhook URL from above - main notification channel]
slackagenturl: [Slack Webhook URL from above - agent failure channel] (optional)
```
### Notification Customization

- as written, you can have the Slack notification customized with either a custom test name and/or a custom message to appear in the notification.
- in your test, if you have a `custom_name` variable, your notification will replace the test name with that name
- in your test if you have a `custom_message` variable, your notification will include that message in the notification


You can now use this advanced webhook with your Runscope tests. Webhook notifications will be sent to the main Slack channel per your Threshold rules except if a test fails because of agent disconnection, in which case it would be sent to the alternate channel

### Additonal Customization

You can modify this code to further customize the notifications you receive. Be sure to create a zip file once you've modified and then re-upload the updated file to AWS Lambda.