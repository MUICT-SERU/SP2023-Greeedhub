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

class Credential:
	"""A class which represents the credential from the API"""
	def __init__(self, type = "", name = "", dict_cred_data = {}):
		self.id = ""
		self.name = name
		self.type = type
		if type != "":
			setattr(self, self.type, dict_cred_data)
		self.created = None
		self.modified = None

	def fromDict(self, credential_dict):
		self.id = credential_dict.get("id", "")
		self.name = credential_dict.get("name", "")
		self.type = credential_dict.get("type", "")
		setattr(self, credential_dict.get("type"), credential_dict.get(credential_dict.get("type")))
		Record = namedtuple("Record", "at, by")
		self.created = Record(credential_dict.get("created").get("at"), credential_dict.get("created").get("by"))
		self.modified = Record(credential_dict.get("modified").get("at"), credential_dict.get("modified").get("by"))

	def __str__(self):
		return ("ID: " + self.id + "\r\n" +
				"Name: " + self.name + "\r\n" +
				"Type: " + self.type + "\r\n" +
				self.type.capitalize() + ": " + str(self.__dict__[self.type]) + "\r\n" +
				"Created: at: " + str(self.created.at) + " by: " + str(self.created.by) + "\r\n" +
				"Modified: at: " + str(self.modified.at) + " by: " + str(self.modified.by) + "\r\n")

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
		return(" \r\n\t  Credential: \r\n\t " + str(self.credential) + "\r\n\t   "+
			   "   Discover: " + str(self.discover) + "\r\n\t   " +
			   "   Scan: " + str(self.scan) + "\r\n\t   " +
			   "   Scope: " + str(self.scope) + "\r\n\t")

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
	def __init__(self, username, password):
		#The API base url
		#self._BASE_URL = "https://api.cloudinsight.alertlogic.com"
		#self._BASE_URL = "https://integration.cloudinsight.alertlogic.com"
		self._BASE_URL = "https://api.product.dev.alertlogic.com"
		self.login(self, username, password)
		self.credentials = list()
		self.roles = list()
		self.sources = list()
		self.credential = None
		self.source = None

	@staticmethod
	def jdefault(o):
		return o.__dict__

	@staticmethod
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

	@staticmethod
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

	def createCredential(self, type, name, dict_cred_data):
		credential = Credential(type, name, dict_cred_data)
		if self.validateCredential(self, credential):
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
		else:
			print "Credential not created"
			return None

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

	def createSource(self, name, collection_type, credential, scope, discover, scan):
		"""Method which creates a source using the API"""
		config = Config(collection_type, credential, scope, discover, scan)
		source = Source(name, config)
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
def options():
	print "\r\n"
	print "=== MENU ==="
	print "1. List Sources"
	print "2. List Credentials"
	print "3. Create Credential"
	print "4. Create Source"
	print "5. Delete Credential"
	print "6. Delete Source"
	print "7. User information"
	print "\r\n"
	opt = input("Select an option or 0 to exit: ")
	print "\r\n"
	return opt

def main():
	#instance of the API object
	print "Welcome to the Alert Logic API"

	print "Please Enter your login information"

	#username = raw_input("Username: ")
	#password = raw_input("Passord: ")
	username = "admin@ozone.com"
	password = "1newP@ssword"
	try:
		print "Logging in the system"
		alAPI = AlertLogicAPI(username, password)
		menu = options()
		while menu != 0:
			if menu == 1:
				print "Listing sources"
				for idx, source in enumerate(alAPI.listSources("source.type=environment")):
					print "Source number " + str(idx)
					print source
			elif menu == 2:
				print "Listing credentials"
				for idx, lcredential in enumerate(alAPI.listCredentials()):
					print "Credential number " + str(idx)
					print lcredential
			elif menu == 3:
				print "Creating credential"
				print "Type: iam_role"
				type = raw_input("Enter the credential type: ")
				print "ARN: arn:aws:iam::948063967832:role/Barry-Product-Integration"
				arn = raw_input("Enter the ARN: ")
				print "External ID: 67013024"
				external_id = raw_input("Enter the external id: ")
				credential_name = raw_input("Enter a credential name: ")
				dict_cred_data = { "arn" : arn, "external_id" : external_id }
				credential = alAPI.createCredential(type, credential_name, dict_cred_data)
			elif menu == 4:
				if len(alAPI.credentials) == 0:
					print "Listing credentials"
					for idx, lcredential in enumerate(alAPI.listCredentials()):
						print "Credential number " + str(idx)
						print lcredential
				print "Creating a source"
				idx = input("Enter the number of the credential: ")
				try:
					credential = alAPI.credentials[idx]
				except IndexError as e:
					print "Invalid number"
					print e
				except TypeError as e:
					print "Enter a number"
					print e
				if credential != None:
					source_name = raw_input("Source name: ")
					print "Collection Type: aws"
					collection_type = raw_input("Collection type: ")
					#include = {"include": [{"type": "vpc","key": "/aws/us-east-1/vpc/vpc-1234"}]}
					include = {}
					discover = bool(raw_input("Discover? Yes or empty for not: "))
					scan = bool(raw_input("Scan? Yes or empty for not: "))
					print alAPI.createSource(source_name, collection_type, credential, include, discover, scan)
				else:
					print "You must created or select a credential first"
			elif menu == 5:
				if len(alAPI.credentials) >= 1:
					print "Deleting Credential"
					idx = input("Enter the number of the credential: ")
					try:
						alAPI.deleteCredential(alAPI.credentials[idx].id)
					except IndexError as e:
						print "Invalid number"
						print e
					except TypeError as e:
						print "Enter a number"
						print e
				else:
					print "List the sources first and check the source number"
			elif menu == 6:
				if len(alAPI.sources) >= 1:
					print "Deleting Source"
					idx = input("Enter the number of the source: ")
					try:
						alAPI.deleteSource(alAPI.sources[idx].id)
					except IndexError as e:
						print "Invalid number"
						print e
					except TypeError as e:
						print "Enter a number"
						print e
				else:
					print "List the sources first and check the source number"
			elif menu == 7:
				print "TOKEN:"
				print alAPI.token
				print "User Information"
				print alAPI.user
			else:
				print "Invalid option"
			menu = options()

		"""
		print "TOKEN:"
		print alAPI.token
		print alAPI.user
		"""
		"""
		print "listing sources"
		for idx, source in enumerate(alAPI.listSources()):
			print "Source number" + str(idx)
			print source
		"""
		"""
		print "Getting Source"
		gotSource = alAPI.getSource("5F5D261D-1790-1005-894D-1247088D0863")
		"""
		"""
		print "Deleting Source"
		alAPI.deleteSource("269769CD-17B8-1005-894D-1247088D0863")
		"""
		"""
		print "listing credentials"
		for idx, lcredential in enumerate(alAPI.listCredentials()):
			print "Credential number " + str(idx)
			print lcredential
		"""
		"""
		print "Getting credential"
		alAPI.getCredential("EACBCFFB-48C0-4F16-A023-8C11EA079FCF")
		"""
		"""
		print "Deleting Credential"
		alAPI.deleteCredential("1D42C9E8-A523-4FBD-BA6F-FB0FE0D22DD5")
		"""
		"""
		print "Creating a source"
		source_name = "Env-Test-Fabio2"
		collection_type = "aws"
		include = {"include": [{"type": "vpc","key": "/aws/us-east-1/vpc/vpc-1234"}]}
		discover = True
		scan = True
		print alAPI.createSource(source_name, collection_type, credential, include, discover, scan)
		print "\r\n"
		"""
		"""
		print "listing sources"
		for idx, source in enumerate(alAPI.listSources()):
			print "Source number " + str(idx)
			print source
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
