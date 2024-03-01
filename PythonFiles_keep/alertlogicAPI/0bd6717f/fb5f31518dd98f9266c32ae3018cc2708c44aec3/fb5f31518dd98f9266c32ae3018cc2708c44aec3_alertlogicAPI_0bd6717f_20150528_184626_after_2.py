#!/usr/bin/python
import json
import requests
from requests.auth import HTTPBasicAuth

class User:
	"""A class which represent the user from the API"""
	def __init__(self, userDict):
		self.user_id = userDict.get("id","")
		self.name = userDict.get("name", "")
		self.email = userDict.get("email", "")
		self.active = True if userDict.get("active", "") == "True" else False
		self.account_id = userDict.get("account_id", "")
		self.created = userDict.get("created") #dictionary keys(at, by)
		self.modified = userDict.get("modified") #dictionary keys(at, by)

	def __str__(self):
		return ("ID: " + self.user_id + "\r\n" +
				"Name: " + self.name + "\r\n" +
				"E-mail: " + self.email + "\r\n" +
				"Active: " + str(self.active) + "\r\n" +
				"Account ID: " + self.account_id + "\r\n" +
				"Created: " + json.dumps(self.created) + "\r\n" +
				"Modified: " + json.dumps(self.modified) + "\r\n")

class IamRole:
	"""A class which represents the iam_role from the API"""
	def __init__(self, arn, external_id):
		self.arn = arn
		self.external_id = external_id

class Credential:
	"""A class which represents the credential from the API"""
	""""credential":{
			"name":"Ozone",
			"type":"iam_role",
			"iam_role":{
				"arn":"arn:aws:iam::481746159046:role/RestrictedRole",
				"external_id":"0000-0012"
			}
		}"""
	def __init__(self, arn, external_id, name = "", cred_type = "iam_role"):
		self.name = name
		self.cred_type = cred_type
		self.iam_role = IamRole(arn, external_id)

class AlertLogicAPI:
	""" Class to make request to the Alert Logic API """
	def __init__(self):
		#The API base url
		self._BASE_URL = "https://api.product.dev.alertlogic.com"
		self.token = ""

	@staticmethod
	def jdefault(o):
		return o.__dict__

	def login(self, username, password):
		authenticate_url = "/aims/v1/authenticate"
		req = requests.post(self._BASE_URL+authenticate_url, auth=HTTPBasicAuth(username, password))
		if (req.status_code == requests.codes.ok):
			response = req.json()
			print json.dumps(response, indent=4)
			self.token = response.get("authentication").get("token","")
			self.user = User(response.get("authentication").get("user"))
		else:
			req.raise_for_status()
	def validateCredentials(self, credential):
		credentials_url = "/cloud_explorer/v1/validate_credentials"
		jsonCredential = {"credential":json.dumps(credential)}
		headers = {"x-iam-auth-token": self.token, "Content-Type": "application/json"}
		req = requests.post(self._BASE_URL+credentials_url, headers=headers, data=jsonCredential)
		if req.status_code == req.codes.ok:
			print "Valid"
			return True
		elif req.status_code == req.codes.forbidden:
			req.raise_for_status()
			print "Error 403"
			return False
		elif req.status_code == req.code.unauthorized:
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
	credential = Credential("arn:aws:iam::481746159046:role/RestrictedRole", "0000-0012", "Ozone")
	print json.dumps(credential, indent=4, default=AlertLogicAPI.jdefault)
	#alAPI.validateCredentials(credential)
	#print alAPI.user
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
