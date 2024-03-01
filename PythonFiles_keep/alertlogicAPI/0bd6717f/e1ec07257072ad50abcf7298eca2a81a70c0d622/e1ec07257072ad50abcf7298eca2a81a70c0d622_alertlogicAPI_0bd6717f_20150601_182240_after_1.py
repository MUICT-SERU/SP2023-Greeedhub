#!/usr/bin/python
import json
import requests
from requests.auth import HTTPBasicAuth
from collections import namedtuple

class User:
	"""A class which represent the user from the API"""
	def __init__(self, userDict):
		self.id = userDict.get("id","")
		self.name = userDict.get("name", "")
		self.email = userDict.get("email", "")
		self.active = userDict.get("active", "")
		self.account_id = userDict.get("account_id", "")
		Record = namedtuple("Record", "at, by")
		self.created = Record(userDict.get("created").get("at"), userDict.get("created").get("by"))
		self.modified = Record(userDict.get("modified").get("at"), userDict.get("modified").get("by"))

	def __str__(self):
		return ("ID: " + self.id + "\r\n" +
				"Name: " + self.name + "\r\n" +
				"E-mail: " + self.email + "\r\n" +
				"Active: " + str(self.active) + "\r\n" +
				"Account ID: " + self.account_id + "\r\n" +
				"Created: at: " + str(self.created.at) + " by: " + str(self.created.by) + "\r\n" +
				"Modified: at: " + str(self.modified.at) + " by: " + str(self.modified.by) + "\r\n")

class IamRole:
	"""A class which represents the iam_role from the API"""
	def __init__(self, arn, external_id):
		self.arn = arn
		self.external_id = external_id

class AWSKey:
	"""A class which represents the aws_key from the API"""
	def __init__(self, access_key_id, secret_access_key):
		self.access_key_id = access_key_id
		self.secret_access_key = secret_access_key

class Role:
	"""A class which represent the role from the API"""
	def __init__(self, account_id = "", name = "", dictPermissions = {}):
		self.account_id = account_id
		self.name = name
		self.permissions = dictPermissions

	def fromDict(self, roleDict):
		self.account_id = roleDict.get("account_id")
		self.name = roleDict.get("name")
		self.id = roleDict.get("id")
		self.permissions = roleDict.get("permissions") #Dictionary of permissions
		Record = namedtuple("Record", "at, by")
		self.created = Record(roleDict.get("created").get("at"), roleDict.get("created").get("by"))
		self.modified = Record(roleDict.get("modified").get("at"), roleDict.get("modified").get("by"))

	def __str__(self):
		return ("ID: " + self.id + "\r\n" +
				"Name: " + self.name + "\r\n" +
				"Account ID: " + self.account_id + "\r\n" +
				"Permissions: " + str(self.permissions) + "\r\n" +
				"Created: at: " + str(self.created.at) + " by: " + str(self.created.by) + "\r\n" +
				"Modified: at: " + str(self.modified.at) + " by: " + str(self.modified.by) + "\r\n")

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
	def __init__(self, arn = "", external_id = "", name = "", type = "", access_key_id = "", secret_access_key = ""):
		self.id = ""
		self.name = name
		self.type = type
		self.iam_role = IamRole(arn, external_id)
		self.aws_key = AWSKey(access_key_id, secret_access_key)
		self.created = None
		self.modified = None

	def fromDict(self, credentialDict):
		self.id = credentialDict.get("id", "")
		self.name = credentialDict.get("name", "")
		self.type = credentialDict.get("type", "")
		if self.type == "iam_role":
			self.iam_role = IamRole(credentialDict.get("iam_role").get("arn"), credentialDict.get("iam_role").get("external_id"))
		elif self.type == "aws_key":
			self.aws_key = AWSKey(credentialDict.get("aws_key").get("access_key_id"), credentialDict.get("aws_key").get("secret_access_key"))
		Record = namedtuple("Record", "at, by")
		self.created = Record(credentialDict.get("created").get("at"), credentialDict.get("created").get("by"))
		self.modified = Record(credentialDict.get("modified").get("at"), credentialDict.get("modified").get("by"))

class Config:
	def __init__(self):
		pass

class AlertLogicAPI:
	""" Class to make request to the Alert Logic API """
	def __init__(self):
		#The API base url
		#self._BASE_URL = "https://integration.cloudinsight.alertlogic.com"
		self._BASE_URL = "https://api.product.dev.alertlogic.com"
		self.token = ""
		self.user = None
		self.credentials = None
		self.roles = []

	@staticmethod
	def jdefault(o):
		return o.__dict__

	def login(self, username, password):
		authenticate_url = "/aims/v1/authenticate"
		req = requests.post(self._BASE_URL+authenticate_url, auth=HTTPBasicAuth(username, password))
		if (req.status_code == requests.codes.ok):
			response = req.json()
			self.token = response.get("authentication").get("token","")
			self.user = User(response.get("authentication").get("user"))
		else:
			print "Error " + str(req.status_code)

	def createRoles(self, role):
		create_roles_url = "/aims/v1/" + role.account_id + "/roles"
		headers = {"X-AIMS-Auth-Token": self.token}
		roleDict = {"name": role.name, "permissions" : role.permissions}
		payload = json.dumps(roleDict)
		req = requests.post(self._BASE_URL+create_roles_url, headers=headers, data=payload)
		if req.status_code == requests.codes.created:
			response = req.json()
			role = Role()
			role.fromDict(roleDict)
			self.roles.append(role)
		else:
			print "Error " + str(req.status_code)

	def deleteRoles(self, roleID):
		delete_role_url = "/aims/v1/" + self.user.account_id + "/roles/" + roleID
		headers = {"X-AIMS-Auth-Token": self.token}
		req = requests.delete(self._BASE_URL+delete_credentials_url, headers=headers)
		print req.text
		print str(req.status_code)
		if req.status_code == requests.codes.no_content:
			self.credential = None
			print "Role deleted"
		else:
			print "Error " + str(req.status_code)

	def listRoles(self):
		list_roles_url = "/aims/v1/" + self.user.account_id + "/roles"
		headers = {"X-AIMS-Auth-Token": self.token}
		req = requests.get(self._BASE_URL+list_roles_url, headers=headers)
		if req.status_code == requests.codes.ok:
			response = req.json()
			self.roles = []
			for roleDict in response.get("roles"):
				role = Role()
				role.fromDict(roleDict)
				self.roles.append(role)
		else:
			print "Error " + str(req.status_code)

	def validateCredentials(self, credential):
		credentials_url = "/cloud_explorer/v1/validate_credentials"
		jsonCredential = {"credential": credential}
		payload = json.dumps(jsonCredential, default=AlertLogicAPI.jdefault)
		headers = {"X-AIMS-Auth-Token": self.token, "Content-Type": "application/json"}
		req = requests.post(self._BASE_URL+credentials_url, headers=headers, data=payload)
		print req.text
		if req.status_code == requests.codes.ok:
			return True
		elif req.status_code == requests.codes.forbidden:
			return False
		elif req.status_code == requests.codes.unauthorized:
			return False
		else:
			print "Error "+ str(req.status_code)
			return False

	def storeCredentials(self, credential):
		store_credential_url = "/sources/v1/" + self.user.account_id + "/credentials"
		jsonCredential = {"credential": credential}
		payload = json.dumps(jsonCredential, default=AlertLogicAPI.jdefault)
		headers = {"X-AIMS-Auth-Token": self.token, "Content-Type": "application/json"}
		req = requests.post(self._BASE_URL+credentials_url, headers=headers, data=payload)
		print req.text
		print str(req.status_code)
		if req.status_code == requests.codes.created:
			credential = Credential()
			self.credential = credential.fromDict(req.json().get("credential"))
			print "Credential Created"
		elif req.status_code == requests.codes.bad_request:
			print "Credential not created. Bad request"
		else:
			print "Error " + str(req.status_code)

	def getCredentials(self, credentialID):
		get_credential_url = "/sources/v1/" + self.user.account_id + "/credentials/" + credentialID
		headers = {"X-AIMS-Auth-Token": self.token}
		req = requests.get(self._BASE_URL+get_credential_url, headers=headers)
		print req.text
		print str(req.status_code)
		if req.status_code == requests.codes.ok:
			credential = Credential()
			self.credential = credential.fromDict(req.json().get("credential"))
		elif req.status_code == requests.codes.not_found:
			print "Credential not found"
		else:
			print "Error "+ str(req.status_code)

	def deleteCredentials(self, credentialID):
		delete_credential_url = "/sources/v1/" + self.user.account_id + "/credentials/" + credentialID
		headers = {"X-AIMS-Auth-Token": self.token}
		req = requests.delete(self._BASE_URL+delete_credentials_url, headers=headers)
		print req.text
		print str(req.status_code)
		if req.status_code == requests.codes.no_content:
			self.credential = None
			print "Credential deleted"
		else:
			print "Error " + str(req.status_code)

	def createSource(self):
		pass

def main():
	alAPI = AlertLogicAPI()
	alAPI.login("admin@ozone.com", "1newP@ssword")
	print "listing roles"
	alAPI.listRoles()
	for role in alAPI.roles:
		print role
	print "creating role"
	permissions = {"*:own:get:*":"allowed", "*:own:list:*":"allowed", "*::get:*":"allowed", "*::list:*":"allowed"}
	role = Role(alAPI.user.account_id, "MyRole", permissions)
	alAPI.createRoles(role)
	print "checking local roles"
	for role in alAPI.roles:
		print role
	print "checking remote roles"
	alAPI.listRoles()
	for role in alAPI.roles:
		print role
	"""print "TOKEN:"
	print alAPI.token
	print "ACCOUNT ID:"
	print alAPI.user.account_id
	credential = Credential("arn:aws:iam::481746159046:role/Administrator", "0000-0012", "Fabio Test", "iam_role")
	if alAPI.validateCredentials(credential):
		#alAPI.storeCredentials(credential)
		print "Valid credential"
	else:
		print "Invalid credential" """

if __name__ == "__main__":
	main()

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
