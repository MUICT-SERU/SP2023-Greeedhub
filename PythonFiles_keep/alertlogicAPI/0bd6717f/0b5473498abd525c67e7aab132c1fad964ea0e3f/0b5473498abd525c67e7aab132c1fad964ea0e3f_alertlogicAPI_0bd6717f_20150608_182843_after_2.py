#!/usr/bin/python
import json
import requests
from requests.auth import HTTPBasicAuth
from collections import namedtuple
from bunch import Bunch

class APIObject(Bunch):
	def __init__(self, obj):
		Bunch.__init__(self, obj)

	def __str__(self):
		return (json.dumps(self, indent = 3,  sort_keys=True))

class AlertLogicAPI:
	""" Class to make request to the Alert Logic API """
	def __init__(self, username, password):
		#The API base url
		#self._BASE_URL = "https://api.cloudinsight.alertlogic.com"
		#self._BASE_URL = "https://integration.cloudinsight.alertlogic.com"
		self._BASE_URL = "https://api.product.dev.alertlogic.com"
		self.login(self, username, password)
		self.credentials = list()
		self.sources = list()

	@staticmethod
	def login(self, username, password):
		"""Method which generates the token for the other requests and gets the user information"""
		authenticate_url = "/aims/v1/authenticate"
		req = requests.post(self._BASE_URL+authenticate_url, auth=HTTPBasicAuth(username, password))
		if req.status_code == requests.codes.ok:
			response = req.json()
			self.token = response.get("authentication").get("token","")
			self.user = APIObject(response.get("authentication").get("user"))
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
		jsonCredential = APIObject({"credential": credential})
		payload = json.dumps(jsonCredential)
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
		"""Method which creates a credential on the system"""
		dict_cred = {"type": type, "name" : name, type : dict_cred_data}
		credential = APIObject(dict_cred)
		if self.validateCredential(self, credential):
			create_credential_url = "/sources/v1/" + self.user.account_id + "/credentials"
			jsonCredential = APIObject({"credential": credential})
			payload = json.dumps(jsonCredential)
			headers = {"X-AIMS-Auth-Token": self.token, "Content-Type": "application/json"}
			req = requests.post(self._BASE_URL+create_credential_url, headers=headers, data=payload)
			if req.status_code == requests.codes.created:
				credential = APIObject(req.json().get("credential"))
				self.credentials.append(credential)
				print "Credential Created"
				return credential
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
		"""Method which lists all the credentials of the user"""
		list_credentials_url = "/sources/v1/" + self.user.account_id + "/credentials?" + filters
		headers = {"X-AIMS-Auth-Token": self.token}
		req = requests.get(self._BASE_URL+list_credentials_url, headers=headers)
		if req.status_code == requests.codes.ok:
			response = req.json()
			self.credentials = list()
			for credObj in response.get("credentials"):
				credential = APIObject(credObj.get("credential"))
				self.credentials.append(credential)
			return self.credentials
		else:
			print "Error " + str(req.status_code)
			req.raise_for_status()

	def getCredential(self, credential_id):
		"""Method which presents the information of a given credential by ID"""
		get_credential_url = "/sources/v1/" + self.user.account_id + "/credentials/" + credential_id
		headers = {"X-AIMS-Auth-Token": self.token}
		req = requests.get(self._BASE_URL+get_credential_url, headers=headers)
		if req.status_code == requests.codes.ok:
			credential = APIObject(req.json().get("credential"))
			return credential
		elif req.status_code == requests.codes.not_found:
			print "Credential not found"
			return None
		else:
			print "Error " + str(req.status_code)
			req.raise_for_status()

	def deleteCredential(self, credential_id):
		"""Method which deletes a credential by ID"""
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
				source = APIObject(sourceObj.get("source"))
				self.sources.append(source)
			return self.sources
		else:
			print "Error " + str(req.status_code)
			req.raise_for_status()

	def createSource(self, name, collection_type, credential, scope, discover, scan):
		"""Method which creates a source using the API"""
		config_dict = {"collection_type" : collection_type, "collection_method" : "api", collection_type : {"credential": credential, "scope" : scope, "discover" : discover, "scan" : scan}}
		config = APIObject(config_dict)
		source_dict = {"name" : name, "config" : config, "type" : "environment", "product_type" : "outcomes", "enabled" : True}
		source = APIObject(source_dict)
		create_source_url = "/sources/v1/" + self.user.account_id + "/sources"
		json_source = APIObject({"source": source})
		payload = json.dumps(json_source)
		headers = {"X-AIMS-Auth-Token" : self.token, "Content-Type" : "application/json"}
		req = requests.post(self._BASE_URL+create_source_url, headers=headers, data=payload)
		if req.status_code == requests.codes.created:
			response = req.json()
			source = APIObject(response.get("source"))
			self.sources.append(source)
			print "Source Created"
			return source
		else:
			print "Error " + str(req.status_code)
			req.raise_for_status()

	def getSource(self, source_id):
		"""Method which gets a source given its ID"""
		get_source_url = "/sources/v1/" + self.user.account_id + "/sources/" + source_id
		headers = {"X-AIMS-Auth-Token": self.token}
		req = requests.get(self._BASE_URL+get_source_url, headers=headers)
		if req.status_code == requests.codes.ok:
			source = APIObject(req.json().get("source"))
			return source
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

	username = raw_input("Username: ")
	password = raw_input("Passord: ")
	#username = "admin@ozone.com"
	#password = "1newP@ssword"
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
					#scope = {"include": [{"type": "vpc","key": "/aws/us-east-1/vpc/vpc-1234"}]}
					scope = {}
					discover = bool(raw_input("Discover? Yes or empty for not: "))
					scan = bool(raw_input("Scan? Yes or empty for not: "))
					source = alAPI.createSource(source_name, collection_type, credential, scope, discover, scan)
					print source
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

	except requests.exceptions.RequestException as e:
		print e

if __name__ == "__main__":
	main()
