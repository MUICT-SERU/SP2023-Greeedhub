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
		return ("USER: \r\n" +
				"  ID: " + self.id + "\r\n" +
				"  Name: " + self.name + "\r\n" +
				"  E-mail: " + self.email + "\r\n" +
				"  Active: " + str(self.active) + "\r\n" +
				"  Account ID: " + self.account_id + "\r\n" +
				"  Created: at: " + str(self.created.at) + " by: " + str(self.created.by) + "\r\n" +
				"  Modified: at: " + str(self.modified.at) + " by: " + str(self.modified.by) + "\r\n")

class IamRole:
	"""A class which represents the iam_role from the API"""
	def __init__(self, arn, external_id):
		self.arn = arn
		self.external_id = external_id

	def __str__(self):
		return ("    ARN: "+self.arn + "\r\n" +
			    "    External ID: " + self.external_id)

class AWSKey:
	"""A class which represents the aws_key from the API"""
	def __init__(self, access_key_id, secret_access_key):
		self.access_key_id = access_key_id
		self.secret_access_key = secret_access_key

	def __str__(self):
		return ("    Access Key ID: " + self.access_key_id + " \r\n " +
			    "    Secret Access Key: " + self.secret_access_key)

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
			printableString += "IAM Role: \r\n" + str(self.iam_role) + "\r\n"
		printableString += ("Created: at: " + str(self.created.at) + " by: " + str(self.created.by) + "\r\n" +
							"Modified: at: " + str(self.modified.at) + " by: " + str(self.modified.by) + "\r\n")
		return printableString

class Source:
	"""Class which represents a source from the API"""
	def __init__(self, name = "", config = None):
		self.type = "environment"
		self.product_type = "outcomes"
		self.name = name
		self.enabled = True
		self.config = config
		self.tags = list()

	def fromDict(self, source_dict):
		self.id = source_dict.get("id")
		self.name = source_dict.get("name")
		self.enabled = source_dict.get("enabled")
		self.product_type = source_dict.get("product_type")
		self.tags.extend(source_dict.get("tags", list()))
		self.type = source_dict.get("type")
		self.host = source_dict.get("host")
		if source_dict.get("status") != None:
			self.status = Status(source_dict.get("status"))
		else:
			self.status = None
		config = Config()
		config.fromDict(source_dict.get("config"))
		self.config = config
		Record = namedtuple("Record", "at, by")
		self.created = Record(source_dict.get("created").get("at"), source_dict.get("created").get("by"))
		self.modified = Record(source_dict.get("modified").get("at"), source_dict.get("modified").get("by"))

	def __str__(self):
		return ("Source: " + "\r\n" +
				"  ID: " + self.id + "\r\n" +
				"  Name: " + self.name + "\r\n" +
				"  Enabled: " + str(self.enabled) + "\r\n" +
				"  Product Type: " + self.product_type + "\r\n" +
				"  Type: " + self.type + "\r\n" +
				"  Tags: " + str(self.tags) + "\r\n" +
				"  Host: " + str(self.host) + "\r\n" +
				"  Status: \r\n" + str(self.status) + "\r\n" +
				"  Config: \r\n" + str(self.config) + "\r\n" +
				"  Created: at: " + str(self.created.at) + " by: " + str(self.created.by) + "\r\n" +
				"  Modified: at: " + str(self.modified.at) + " by: " + str(self.modified.by) + "\r\n")

class Config:
	"""Class which represents a source configuration from the API"""
	def __init__(self, collection_type = "", credential = None, scope = None, discover = True, scan = True):
		self.collection_method = "api"
		self.collection_type = collection_type
		if credential != None:
			third_config = ThirdConfig()
			third_config.aws(credential, scope, discover, scan)
			setattr(self, collection_type, third_config)

	def fromDict(self, config_dict):
		self.collection_method = config_dict.get("collection_method")
		self.collection_type = config_dict.get("collection_type")
		setattr(self, config_dict.get("collection_type"), config_dict.get(config_dict.get("collection_type")))

	def __str__(self):
		return ("    Collection Method: " + self.collection_method + "\r\n" +
				"    Collection Type: " + self.collection_type + "\r\n" +
				"    " + self.collection_type.capitalize() + ": " + str(self.__dict__[self.collection_type]) + "\r\n")

class ThirdConfig:
	"""Class which represents a third-party environment config"""
	def aws(self, credential, scope = None, discover = True, scan = True):
		self.credential = credential
		self.discover = discover
		self.scan = scan
		self.scope = scope

	def __str__(self):
		return(" \r\n\t   Credential: " + str(self.credential) + "\r\n\t   "+
			   "Discover: " + str(self.discover) + "\r\n\t   " +
			   "Scan: " + str(self.scan) + "\r\n\t   " +
			   "Scope: " + str(scope) + "\r\n\t")

class Status:
	""" Class which represents the status of a source from the API"""
	def __init__(self, status_dict):
		self.status = status_dict.get("status")
		self.details = list()
		self.details.extend(status_dict.get("details"))
		self.timestamp = status_dict.get("timestamp")
		self.updated = status_dict.get("updated")

	def __str__(self):
		return ("    Status: " + str(self.status) + "\r\n" +
				"    Details: " + str(self.details) + "\r\n" +
				"    Timestamp: " + str(self.timestamp) + "\r\n" +
				"    Updated: " + str(self.updated))


class AlertLogicAPI:
	""" Class to make request to the Alert Logic API """
	def __init__(self):
		#The API base url
		#self._BASE_URL = "https://integration.cloudinsight.alertlogic.com"
		self._BASE_URL = "https://api.product.dev.alertlogic.com"
		self.token = ""
		self.user = None
		self.credentials = list()
		self.roles = list()
		self.sources = list()

	@staticmethod
	def jdefault(o):
		return o.__dict__

	def login(self, username, password):
		"""Method which generates the Token for the other requests and gets the user information"""
		authenticate_url = "/aims/v1/authenticate"
		req = requests.post(self._BASE_URL+authenticate_url, auth=HTTPBasicAuth(username, password))
		if req.status_code == requests.codes.ok:
			response = req.json()
			self.token = response.get("authentication").get("token","")
			self.user = User(response.get("authentication").get("user"))
			print "User authenticated"
			return self.user
		elif req.status_code == requests.codes.service_unavailable:
			print "Service Unavailable, please try later!"
			req.raise_for_status()
		else:
			print "Error " + str(req.status_code)
			req.raise_for_status()

	def validateCredential(self, credential):
		"""Method which validate credentials"""
		credentials_url = "/cloud_explorer/v1/validate_credentials"
		jsonCredential = {"credential": credential}
		payload = json.dumps(jsonCredential, default=self.jdefault)
		headers = {"X-AIMS-Auth-Token": self.token, "Content-Type": "application/json"}
		req = requests.post(self._BASE_URL+credentials_url, headers=headers, data=payload)
		if req.status_code == requests.codes.ok:
			print "Valid credential"
			return True
		elif req.status_code == requests.codes.forbidden:
			print "Invalid credential"
			return False
		elif req.status_code == requests.codes.unauthorized:
			print "Invalid request"
			return False
		elif req.status_code == requests.codes.service_unavailable:
			print "Service unavailable, please try later!"
			req.raise_for_status()
			return False
		else:
			print "Error "+ str(req.status_code)
			req.raise_for_status()
			return False

	def createCredential(self, credential):
		create_credential_url = "/sources/v1/" + self.user.account_id + "/credentials"
		jsonCredential = {"credential": credential}
		payload = json.dumps(jsonCredential, default=self.jdefault)
		headers = {"X-AIMS-Auth-Token": self.token, "Content-Type": "application/json"}
		req = requests.post(self._BASE_URL+create_credential_url, headers=headers, data=payload)
		if req.status_code == requests.codes.created:
			credential = Credential()
			credential.fromDict(req.json().get("credential"))
			self.credential = credential
			print "Credential Created"
			return self.credential
		elif req.status_code == requests.codes.bad_request:
			print "Credential not created. Bad request"
			req.raise_for_status()
		else:
			print "Error " + str(req.status_code)
			req.raise_for_status()

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
			return self.credentials
		else:
			print "Error " + str(req.status_code)
			req.raise_for_status()

	def getCredential(self, credential_id):
		get_credential_url = "/sources/v1/" + self.user.account_id + "/credentials/" + credential_id
		headers = {"X-AIMS-Auth-Token": self.token}
		req = requests.get(self._BASE_URL+get_credential_url, headers=headers)
		if req.status_code == requests.codes.ok:
			credential = Credential()
			credential.fromDict(req.json().get("credential"))
			self.credential = credential
			return self.credential
		elif req.status_code == requests.codes.not_found:
			print "Credential not found"
			return None
		else:
			print "Error "+ str(req.status_code)
			req.raise_for_status()

	def deleteCredential(self, credential_id):
		delete_credential_url = "/sources/v1/" + self.user.account_id + "/credentials/" + credential_id
		headers = {"X-AIMS-Auth-Token": self.token}
		req = requests.delete(self._BASE_URL+delete_credential_url, headers=headers)
		if req.status_code == requests.codes.no_content:
			self.credential = None
			print "Credential deleted"
		else:
			print "Error " + str(req.status_code)
			req.raise_for_status()

	def listSources(self, filters=""):
		"""Method which list all the logged user sources"""
		list_sources_url = "/sources/v1/" + self.user.account_id + "/sources?" + filters
		headers = {"X-AIMS-Auth-Token": self.token}
		req = requests.get(self._BASE_URL+list_sources_url, headers=headers)
		if req.status_code == requests.codes.ok:
			response = req.json()
			self.sources = list()
			for sourceObj in response.get("sources"):
				source = Source()
				source.fromDict(sourceObj.get("source"))
				self.sources.append(source)
			return self.sources
		else:
			print "Error " + str(req.status_code)
			req.raise_for_status()

	def createSource(self, source):
		"""Method which creates a source using the API"""
		create_source_url = "/sources/v1/" + self.user.account_id + "/sources"
		json_source = {"source": source}
		payload = json.dumps(json_source, default=self.jdefault)
		headers = {"X-AIMS-Auth-Token": self.token, "Content-Type": "application/json"}
		req = requests.post(self._BASE_URL+create_source_url, headers=headers, data=payload)
		if req.status_code == requests.codes.created:
			response = req.json()
			source = Source()
			source.fromDict(response.get("source"))
			self.sources.append(source)
			self.source = source
			print "Source Created"
			return self.source
		else:
			print "Error " + str(req.status_code)
			req.raise_for_status()

	def getSource(self, source_id):
		"""Method which gets a source given its ID"""
		get_source_url = "/sources/v1/" + self.user.account_id + "/sources/" + source_id
		headers = {"X-AIMS-Auth-Token": self.token}
		req = requests.get(self._BASE_URL+get_source_url, headers=headers)
		if req.status_code == requests.codes.ok:
			source = Source()
			source.fromDict(req.json().get("source"))
			self.source = source
			return self.source
		elif req.status_code == requests.codes.not_found:
			print "Source not found"
			return None
		else:
			print "Error "+ str(req.status_code)
			req.raise_for_status()

	def deleteSource(self, source_id):
		"""Method which deletes a source"""
		delete_source_url = "/sources/v1/" + self.user.account_id + "/sources/" + source_id
		headers = {"X-AIMS-Auth-Token": self.token}
		req = requests.delete(self._BASE_URL+delete_source_url, headers=headers)
		if req.status_code == requests.codes.no_content:
			self.source = None
			print "Source deleted"
		else:
			print "Error " + str(req.status_code)
			req.raise_for_status()

def main():
	#instance of the API object
	alAPI = AlertLogicAPI()
	try:
		print "Log in the system"
		alAPI.login("admin@ozone.com", "1newP@ssword")

		"""
		print "Getting Source"
		alAPI.getSource("5F5D261D-1790-1005-894D-1247088D0863")
		"""

		#"""
		print "listing sources"
		for idx, source in enumerate(alAPI.listSources()):
			print "Source number" + str(idx)
			print source
		#"""

		"""
		print "Deleting Source"
		alAPI.deleteSource("BA2B9372-17A4-1005-894D-1247088D0863")
		"""

		"""
		print "Getting credential"
		alAPI.getCredential("EACBCFFB-48C0-4F16-A023-8C11EA079FCF")
		"""

		"""
		print "Getting credential"
		alAPI.getCredential("EACBCFFB-48C0-4F16-A023-8C11EA079FCF")
		"""

		"""
		print "TOKEN:"
		print alAPI.token
		print alAPI.user
		"""

		"""
		print "listing credentials"
		for idx, lcredential in enumerate(alAPI.listCredentials()):
			print "Credential number " + str(idx)
			print lcredential
		"""

		#"""
		print "Validating credential"
		#credential = Credential("arn:aws:iam::481746159046:role/CloudInsightRole", "10000001", "Fabio Test", "iam_role")
		credential = Credential("arn:aws:iam::948063967832:role/Barry-Product-Integration", "67013024", "Fabio Test", "iam_role")
		if alAPI.validateCredential(credential):
			vcredential = alAPI.createCredential(credential)
			#"""
			print "Creating a source"
			include = {"include": [{"type": "vpc","key": "/aws/us-east-1/vpc/vpc-1234"}]}
			config = Config("aws", vcredential, include, False, False)
			source = Source("Env-Test-Fabio", config)
			print alAPI.createSource(source)
			print "\r\n"
			#"""
		else:
			print "Invalid credential"
			exit(1)
		#"""

		#"""
		print "listing sources"
		for idx, source in enumerate(alAPI.listSources()):
			print "Source number" + str(idx)
			print source
		#"""


		"""
		print "Deleting Credential"
		alAPI.deleteCredential("D4CB7E3C-B090-48E7-B933-2A913DAF9480")
		"""

		"""
		print "listing credentials"
		for idx, lcredential in enumerate(alAPI.listCredentials()):
			print "Credential number " + str(idx)
			print lcredential
		"""

	except requests.exceptions.RequestException as e:
		print e

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
