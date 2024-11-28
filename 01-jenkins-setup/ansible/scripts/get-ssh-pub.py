import boto3                               # Imports the boto3 library, which provides an interface for AWS services
import json                                # Imports the json library, which allows working with JSON data
import sys                                 # Imports the sys library, which provides access to system-specific parameters and functions

client = boto3.client('ssm', region_name='us-west-2')  # Creates a client for the AWS Systems Manager (SSM) service in the 'us-west-2' region
response = client.get_parameter(                       # Calls the get_parameter method on the SSM client
    Name=sys.argv[1],                                  # Passes the first command-line argument as the parameter name
    WithDecryption=True                                # Specifies that the parameter should be decrypted if it is encrypted
)
print(response['Parameter']['Value'])                  # Prints the value of the parameter to the console
