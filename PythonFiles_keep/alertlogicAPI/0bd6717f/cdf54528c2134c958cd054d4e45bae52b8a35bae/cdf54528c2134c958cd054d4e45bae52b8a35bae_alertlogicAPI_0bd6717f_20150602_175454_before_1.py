#!/usr/bin/python
import json
import requests
from requests.auth import HTTPBasicAuth
from collections import namedtuple

class User:
	"""A class which represent the user from the API"""
	def __init__(self, user_dict):
		self.id = user_dict.get("id","")
		self.name = user_dict.get("name", "")
		self.email = user_dict.get("email", "")
		self.active = user_dict.get("active", "")
		self.account_id = user_dict.get("account_id", "")
		Record = namedtuple("Record", "at, by")
		self.created = Record(user_dict.get("created").get("at"), user_dict.get("created").get("by"))
		self.modified = Record(user_dict.get("modified").get("at"), user_dict.get("modified").get("by"))

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

	def __str__(self):
		return ("ARN: "+self.arn + " \ " +
			    "External ID: "+self.external_id)

class AWSKey:
	"""A class which represents the aws_key from the API"""
	def __init__(self, access_key_id, secret_access_key):
		self.access_key_id = access_key_id
		self.secret_access_key = secret_access_key

	def __str__(self):
		return ("Access Key ID: "+self.access_key_id + " \ " +
			    "Secret Access Key: "+self.secret_access_key)

class Role:
	"""A class which represent the role from the API"""
	def __init__(self, account_id = "", name = "", dictPermissions = {}):
		self.account_id = account_id
		self.name = name
		self.permissions = dictPermissions

	def fromDict(self, role_dict):
		self.account_id = role_dict.get("account_id")
		self.name = role_dict.get("name")
		self.id = role_dict.get("id")
		self.permissions = role_dict.get("permissions") #Dictionary of permissions
		Record = namedtuple("Record", "at, by")
		self.created = Record(role_dict.get("created").get("at"), role_dict.get("created").get("by"))
		self.modified = Record(role_dict.get("modified").get("at"), role_dict.get("modified").get("by"))

	def __str__(self):
		return ("ID: " + self.id + "\r\n" +
				"Name: " + self.name + "\r\n" +
				"Account ID: " + self.account_id + "\r\n" +
				"Permissions: " + str(self.permissions) + "\r\n" +
				"Created: at: " + str(self.created.at) + " by: " + str(self.created.by) + "\r\n" +
				"Modified: at: " + str(self.modified.at) + " by: " + str(self.modified.by) + "\r\n")

class Credential:
	"""A class which represents the credential from the API"""
	def __init__(self, arn = "", external_id = "", name = "", type = "", access_key_id = "", secret_access_key = ""):
		self.id = ""
		self.name = name
		self.type = type
		self.iam_role = IamRole(arn, external_id)
		self.aws_key = AWSKey(access_key_id, secret_access_key)
		self.created = None
		self.modified = None

	def fromDict(self, credential_dict):
		self.id = credential_dict.get("id", "")
		self.name = credential_dict.get("name", "")
		self.type = credential_dict.get("type", "")
		if self.type == "iam_role":
			self.iam_role = IamRole(credential_dict.get("iam_role").get("arn"), credential_dict.get("iam_role").get("external_id"))
		elif self.type == "aws_key":
			self.aws_key = AWSKey(credential_dict.get("aws_key").get("access_key_id"), credential_dict.get("aws_key").get("secret_access_key"))
		Record = namedtuple("Record", "at, by")
		self.created = Record(credential_dict.get("created").get("at"), credential_dict.get("created").get("by"))
		self.modified = Record(credential_dict.get("modified").get("at"), credential_dict.get("modified").get("by"))

	def __str__(self):
		printableString = ("ID: " + self.id + "\r\n" +
						  "Name: " + self.name + "\r\n" +
						  "Type: " + self.type + "\r\n")
		if self.type == "aws_key":
			printableString += "AWS-Key: " + str(self.aws_key) + "\r\n"
		else:
			printableString += "IAM Role: " + str(self.iam_role) + "\r\n"
		printableString += ("Created: at: " + str(self.created.at) + " by: " + str(self.created.by) + "\r\n" +
							"Modified: at: " + str(self.modified.at) + " by: " + str(self.modified.by) + "\r\n")
		return printableString

class Source:
	"""Class which represents a source from the API"""
	"""{
    "source": {
        "config": {
            "collection_method": "api",
            "collection_type": "aws" | "gce" | "azure",       /* collection_type specifies wich JSON key contains configuration. */
            "aws": {},
        "enabled": true,
        "name": "route105-east-1",
        "product_type": "outcomes",
        "tags": [],
        "type": "environment"
    }
}"""
	def __init__(self):
		self.id = ""
		self.type = "environment"
		self.product_type = "outcomes"
		self.name = ""
		self.enabled = True
		self.config = None
		self.tags = list()
		self.status = None

	def fromDict(self, source_dict):
		self.id = source_dict.get("id")
		self.name = source_dict.get("name")
		self.enabled = source_dict.get("enabled")
		self.product_type = source_dict.get("product_type")
		self.tags.extend(source_dict.get("tags"))
		self.type = source_dict.get("type")
		self.host = source_dict.get("host")
		self.status = Status(user_dict.get("status"))
		self.config = Config(user_dict.get("config"))
		Record = namedtuple("Record", "at, by")
		self.created = Record(source_dict.get("created").get("at"), source_dict.get("created").get("by"))
		self.modified = Record(source_dict.get("modified").get("at"), source_dict.get("modified").get("by"))

	def __str__(self):
		return ("Config: " + "\r\n" +
				"  ID: " + self.id + "\r\n" +
				"  Name: " + self.name + "\r\n" +
				"  Enabled: " + str(self.enabled) + "\r\n" +
				"  Product Type: " + self.product_type + "\r\n" +
				"  Type: " + self.type + "\r\n" +
				"  Tags: " + self.tags + "\r\n" +
				"  Host: " + self.host + "\r\n" +
				"  Status: " + self.status + "\r\n" +
				"  Config: " + self.config + "\r\n" +
				"  Created: at: " + str(self.created.at) + " by: " + str(self.created.by) + "\r\n" +
				"  Modified: at: " + str(self.modified.at) + " by: " + str(self.modified.by) + "\r\n")

class Config:
	"""Class which represents a source configuration from the API"""
	"""
	"config": {
            "collection_method": "api",
            "collection_type": "aws" | "gce" | "azure",       /* collection_type specifies wich JSON key contains configuration. */
            "aws": {
                "credential": {
                    "id": "4F112A6E-F678-1004-9B87-7831C1BE64D2"
                },
                /* Note that the following attributes could become a policy in a future */
                "discover": true,
                "scan": true,
                "scope": {
                    "include": [
                        {
                            "type": "vpc",
                            "key": "/aws/us-east-1/vpc/vpc-1234"
                        }
                    ]
                }
            }
        }
		"""
	def __init__(self, config_dict):
		self.collection_method = config_dict.get("collection_method")
		self.collection_type = config_dict.get("collection_type")
		setattr(Config, config_dict.get("collection_type"), config_dict.get(config_dict.get("collection_type")))

	def __str__(self):
		return ("  Collection Method: " + self.collection_method + "\r\n" +
				"  Collection Type: " + self.collection_type + "\r\n" +
				"  " + self.collection_type.capitalize() + ": " + self.__dict[self.collection_type] + "\r\n" +
				"  Updated: " + self.updated + "\r\n")


class Status:
	"Class which represents the status of a source from the API"""
	def __init__(self, status_dict):
		self.status = status_dict.get("status")
		self.details = list()
		self.details.extend(status_dict.get("details"))
		self.timestamp = status_dict.get("timestamp")
		self.updated = status_dict.get("updated")

	def __str__(self):
		return ("  Status: " + self.status + "\r\n" +
				"  Details: " + self.details + "\r\n" +
				"  Timestamp: " + self.timestamp + "\r\n" +
				"  Updated: " + self.updated + "\r\n")


class AlertLogicAPI:
	""" Class to make request to the Alert Logic API """
	def __init__(self):
		#The API base url
		#self._BASE_URL = "https://integration.cloudinsight.alertlogic.com"
		self._BASE_URL = "https://api.product.dev.alertlogic.com"
		self.token = ""
		self.user = None
		self.credentials = None
		self.roles = list()

	@staticmethod
	def jdefault(o):
		return o.__dict__

	def login(self, username, password):
		"""Method which generates the Token for the other requests"""
		authenticate_url = "/aims/v1/authenticate"
		req = requests.post(self._BASE_URL+authenticate_url, auth=HTTPBasicAuth(username, password))
		if (req.status_code == requests.codes.ok):
			response = req.json()
			self.token = response.get("authentication").get("token","")
			self.user = User(response.get("authentication").get("user"))
		else:
			print "Error " + str(req.status_code)

	def createRoles(self, role):
		"""getting a 403 Error"""
		create_roles_url = "/aims/v1/" + role.account_id + "/roles"
		headers = {"X-AIMS-Auth-Token": self.token}
		role_dict = {"name": role.name, "permissions" : role.permissions}
		payload = json.dumps(role_dict, default=AlertLogicAPI.jdefault)
		req = requests.post(self._BASE_URL+create_roles_url, headers=headers, data=payload)
		if req.status_code == requests.codes.created:
			response = req.json()
			role = Role()
			role.fromDict(role_dict)
			self.roles.append(role)
		else:
			print "Error " + str(req.status_code)

	def deleteRoles(self, role_id):
		"""Untested"""
		delete_role_url = "/aims/v1/" + self.user.account_id + "/roles/" + role_id
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
		"""Method which lists all the roles of the logged user"""
		list_roles_url = "/aims/v1/" + self.user.account_id + "/roles"
		headers = {"X-AIMS-Auth-Token": self.token}
		req = requests.get(self._BASE_URL+list_roles_url, headers=headers)
		if req.status_code == requests.codes.ok:
			response = req.json()
			self.roles = list()
			for role_dict in response.get("roles"):
				role = Role()
				role.fromDict(role_dict)
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

	def listCredentials(self, filters=""):
		list_credentials_url = "/sources/v1/" + self.user.account_id + "/credentials?" + filters
		headers = {"X-AIMS-Auth-Token": self.token}
		req = requests.get(self._BASE_URL+list_credentials_url, headers=headers)
		if req.status_code == requests.codes.ok:
			response = req.json()
			self.credentials = list()
			for credObj in response.get("credentials"):
				credential = Credential()
				credential.fromDict(credObj.get("credential"))
				self.credentials.append(credential)
		else:
			print "Error " + str(req.status_code)

	def getCredential(self, credential_id):
		get_credential_url = "/sources/v1/" + self.user.account_id + "/credentials/" + credential_id
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

	def deleteCredentials(self, credential_id):
		delete_credential_url = "/sources/v1/" + self.user.account_id + "/credentials/" + credential_id
		headers = {"X-AIMS-Auth-Token": self.token}
		req = requests.delete(self._BASE_URL+delete_credentials_url, headers=headers)
		print req.text
		print str(req.status_code)
		if req.status_code == requests.codes.no_content:
			self.credential = None
			print "Credential deleted"
		else:
			print "Error " + str(req.status_code)

	def listSources(self, filters=""):
		list_sources_url = "/sources/v1/" + self.user.account_id + "/sources?" + filters
		headers = {"X-AIMS-Auth-Token": self.token}
		req = requests.get(self._BASE_URL+list_sources_url, headers=headers)
		if req.status_code == requests.codes.ok:
			response = req.json()
			self.sources = list()
			for credObj in response.get("credentials"):
				credential = Credential()
				credential.fromDict(credObj.get("credential"))
				self.credentials.append(credential)
		else:
			print "Error " + str(req.status_code)
	def createSource(self):
		pass

def main():
	#instance of the API object
	alAPI = AlertLogicAPI()

	print "Log in the system"
	alAPI.login("admin@ozone.com", "1newP@ssword")

	"""
	print "listing credentials"
	alAPI.listCredentials()
	for credential in alAPI.credentials:
		print credential
	"""

	"""
	print "listing roles"
	alAPI.listRoles()
	for role in alAPI.roles:
		print role
	"""

	"""
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
	"""


	print "TOKEN:"
	print alAPI.token
	print "ACCOUNT ID:"
	print alAPI.user.account_id


	"""
	print "Validating credential"
	credential = Credential("arn:aws:iam::481746159046:role/CloudInsightRole", "10000001", "Fabio Test", "iam_role")
	#credential = Credential("arn:aws:iam::948063967832:role/Barry-Product-Integration", "67013024", "Fabio Test", "iam_role")
	if alAPI.validateCredentials(credential):
		alAPI.storeCredentials(credential)
	else:
		print "Invalid credential"
	"""

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
