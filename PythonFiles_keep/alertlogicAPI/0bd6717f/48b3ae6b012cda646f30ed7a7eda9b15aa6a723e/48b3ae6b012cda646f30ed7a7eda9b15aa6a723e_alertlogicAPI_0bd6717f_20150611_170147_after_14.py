#!/usr/bin/python
import json
import requests
from requests.auth import HTTPBasicAuth
from bunch import Bunch

class APIObject(Bunch):
	def __init__(self, obj):
		Bunch.__init__(self, obj)

	def __str__(self):
		return (json.dumps(self, indent = 3,  sort_keys=True))

class CloudInsightAPI:
	""" Class to make request to the Alert Logic API """
	def __init__(self):
		#The API base url
		#self._BASE_URL = "https://api.cloudinsight.alertlogic.com"
		self._BASE_URL = "https://api.product.dev.alertlogic.com"
		self.credentials = dict()
		self.sources = dict()
		self.user = None
		self.token = ""

	def login(self, username, password):
		"""Method which generates the token for the other requests and gets the user information"""
		authenticate_url = "/aims/v1/authenticate"
		req = requests.post(self._BASE_URL+authenticate_url, auth=HTTPBasicAuth(username, password))
		if req.status_code == requests.codes.ok:
			response = req.json()
			self.token = response.get("authentication").get("token","")
			self.user = APIObject(response.get("authentication").get("user"))
			print "User authenticated"
			return True
		elif req.status_code == requests.codes.unauthorized:
			print "The login information is invalid."
			req.raise_for_status()
			return False
		elif req.status_code == requests.codes.service_unavailable:
			print "Service Unavailable, please try later!"
			req.raise_for_status()
			return False
		else:
			print "Error " + str(req.status_code)
			req.raise_for_status()
			return False

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
			req.raise_for_status()
			return False
		elif req.status_code == requests.codes.unauthorized:
			print "Invalid request"
			req.raise_for_status()
			return False
		elif req.status_code == requests.codes.service_unavailable:
			print "Service unavailable, please try later!"
			req.raise_for_status()
			return False
		elif req.status_code == requests.codes.internal_server_error:
			print "Internal Server Error. Possible wrong JSON object"
			print "Credential not created"
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
				self.credentials[credential.id] = credential
				print "Credential Created"
				return credential
			elif req.status_code == requests.codes.bad_request:
				print "Credential not created. Bad request"
				req.raise_for_status()
				return None
			elif req.status_code == requests.codes.service_unavailable:
				print "Service unavailable, please try later!"
				req.raise_for_status()
				return None
			elif req.status_code == requests.codes.internal_server_error:
				print "Internal Server Error. Possible wrong JSON object"
				print "Credential not created"
				req.raise_for_status()
				return None
			else:
				print "Error " + str(req.status_code)
				req.raise_for_status()
				return None
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
			self.credentials = dict()
			for credObj in response.get("credentials"):
				credential = APIObject(credObj.get("credential"))
				self.credentials[credential.id] = credential
			return self.credentials
		elif req.status_code == requests.codes.service_unavailable:
			print "Service unavailable, please try later!"
			req.raise_for_status()
			return dict()
		else:
			print "Error " + str(req.status_code)
			req.raise_for_status()
			return dict()

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
			req.raise_for_status()
			return None
		elif req.status_code == requests.codes.service_unavailable:
			print "Service unavailable, please try later!"
			req.raise_for_status()
			return None
		else:
			print "Error " + str(req.status_code)
			req.raise_for_status()
			return None

	def deleteCredential(self, credential_id):
		"""Method which deletes a credential by ID"""
		delete_credential_url = "/sources/v1/" + self.user.account_id + "/credentials/" + credential_id
		headers = {"X-AIMS-Auth-Token": self.token}
		req = requests.delete(self._BASE_URL+delete_credential_url, headers=headers)
		if req.status_code == requests.codes.no_content:
			self.credential = None
			print "Credential deleted"
		elif req.status_code == requests.codes.service_unavailable:
			print "Service unavailable, please try later!"
			req.raise_for_status()
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
			self.sources = dict()
			for sourceObj in response.get("sources"):
				source = APIObject(sourceObj.get("source"))
				self.sources[source.id] = source
			return self.sources
		elif req.status_code == requests.codes.service_unavailable:
			print "Service unavailable, please try later!"
			req.raise_for_status()
			return dict()
		else:
			print "Error " + str(req.status_code)
			req.raise_for_status()
			return dict()

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
			self.sources[source.id] = source
			print "Source Created"
			return source
		elif req.status_code == requests.codes.internal_server_error:
			print "Internal Server Error. Possible wrong JSON object"
			print "Source not created"
			req.raise_for_status()
			return None
		elif req.status_code == requests.codes.service_unavailable:
			print "Service unavailable, please try later!"
			req.raise_for_status()
			return None
		else:
			print "Error " + str(req.status_code)
			req.raise_for_status()
			return None

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
			req.raise_for_status()
			return None
		elif req.status_code == requests.codes.service_unavailable:
			print "Service unavailable, please try later!"
			req.raise_for_status()
			return None
		else:
			print "Error "+ str(req.status_code)
			req.raise_for_status()
			return None

	def deleteSource(self, source_id):
		"""Method which deletes a source"""
		delete_source_url = "/sources/v1/" + self.user.account_id + "/sources/" + source_id
		headers = {"X-AIMS-Auth-Token": self.token}
		req = requests.delete(self._BASE_URL+delete_source_url, headers=headers)
		if req.status_code == requests.codes.no_content:
			print "Source deleted"
		elif req.status_code == requests.codes.service_unavailable:
			print "Service unavailable, please try later!"
			req.raise_for_status()
		else:
			print "Error " + str(req.status_code)
			req.raise_for_status()
