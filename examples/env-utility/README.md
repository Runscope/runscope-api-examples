# Runscope Environment Export/Import Scripts

These two scripts are designed to facilitate copying of environments from Runscope.

## Prerequisites
To use these scripts, you need to get a Runscope Access Token. For more information on getting a token, check out: [https://www.runscope.com/docs/api/authentication](https://www.runscope.com/docs/api/authentication).

You can use the personal access token once you have created an application.

## Configuration

Once you have the token, fill the variables in the runscope_config.py file

* `master_bucket_key`:  The bucket key to export from.
* `master_env_id`:  The UUID of the shared environment to export.
* `runscope_token`:  Runscope API token.
* `runscope_dest_bucket`:  The bucket to copy to.

## Usage

### Export Environment

Usage: `python export_env.py`

That will export a file with name of the environment to current directory.

You can also override default settings with various flags:

* `-c CONFIG_FILE_NAME`: overrides the default config file (don't include ".py").
* `-b BUCKET_ID`: overrides the bucket ID in config file.
* `-e ENV_UUID`: overrides the Environment UUID in config file.
* `-t TEST_UUID`: if you specify a Test UUID, you can export a test environment (using ENV_UUID to go with the test).
* `-k RUNSCOPE_TOKEN`: overrides the Runscope token in config file.

### Import Environment

Usage: `python import_env.py <environment_name.json>`

You can override default settings with various flags:

* `-c CONFIG_FILE_NAME`: overrides the default config file (don't include ".py").
* `-b BUCKET_ID`: overrides the bucket ID in config file.
* `-e ENV_UUID`: overrides the Environment UUID in config file -- if you specify an environment UUID you also need to do the `-m` (modify) flag to indicate that you want to modify the environment.
* `-t TEST_UUID`: if you specify a Test UUID, you can import an environment to a test.
* `-k RUNSCOPE_TOKEN`: overrides the Runscope token in config file.
* `-m`: add this flag to indicate that you are modifying the environment specified with the `-e ENV_UUID` flag.


