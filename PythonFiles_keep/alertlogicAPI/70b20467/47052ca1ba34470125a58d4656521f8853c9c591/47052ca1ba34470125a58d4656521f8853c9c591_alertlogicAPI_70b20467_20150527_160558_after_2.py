#!/usr/bin/python

import requests
from requests.auth import HTTPBasicAuth

class User:
	"""A class which represent the user from the API"""
	def __init__(self, userDict):
		self.id = userDict["id"]
		self.name = userDict["name"]
		self.email = userDict["email"]
		self.active = userDict["active"]
		self.account_id = userDict["account_id"]
		self.created = userDict["created"] #dictionary keys(at, by)
		self.modified = userDict["modified"] #dictionary keys(at, by)

class AlertLogicAPI:
	""" Class to make request to the Alert Logic API """
	def __init__(self):
		#The API base url
		self._BASE_URL = "https://api.product.dev.alertlogic.com"
		self.token = ""
	
	def login(self, username, password):
		authenticate_url = "/aims/v1/authenticate"
		req = requests.post(self._BASE_URL+authenticate_url, auth=HTTPBasicAuth(username, password))
		if (req.status_code == requests.codes.ok):
			response = req.json()
			self.token = response["authentication"]["token"]
			self.user = User(response["authentication"]["user"])
		else:
			req.raise_for_status()
	def validateCredentials(self, name, arn, external_id, credType = "iam_role", ):
		credentials_url = "/cloud_explorer/v1/validate_credentials"
		credential = {"credential":{"name":name, "type": credType, "iam_role":{"arn":arn, "external_id": external_id}}}
		headers = {"x-iam-auth-token": self.token, "Content-Type": "application/json"}
		req = requests.post(self._BASE_URL+credentials_url, headers=headers, data=credentials)
		if (req.status_code == req.codes.ok):
			return True
		elif(req.status_code == req.codes.forbidden):
			req.raise_for_status()
			print "Error 403"
			return False
		elif(req.status_code == req.code.unauthorized):
			print "Error 401"
			req.raise_for_status()
			return False
		else:
			req.raise_for_status()
			print "Error "+req.status_code
			return False
	
def main():
	#alAPI = AlertLogicAPI()
	#alAPI.login("admin@ozone.com", "1newP@ssword")
	#print alAPI.token
	#print alAPI.user.name
	#print alAPI.user.email

if __name__ == "__main__":
	main()

"""
	{  
   		"credential":{  
      		"name":"Ozone",
      		"type":"iam_role",
      		"iam_role":{  
         		"arn":"arn:aws:iam::123456789016:role/outcomes_role",
         		"external_id":"0000-0001"
      		}
   		}
	}
"""
# Script to create an environment

# 1) Authenticate
# 	1.1 Send a request to /aims/v1/authenticate
#		(header-field: Authorization - http basic auth string)
#	1.2 Use the received token on the header as x-aims-auth-token
#		for all the other requests
# 2) Create credentials
#	2.1 Read user credentials
#	2.2 Validade the user credentials
#		2.2.1 Send a request to /cloud_explorer/v1/validate_credentials
#	2.3 Store user credentials
#		2.3.1 Send a request to /sources/v1/:account_id/credential
# 3) Create environment
#	3.1 Create the source
#		3.1.1 Send a request to /sources/v1/:account_id/sources
#	