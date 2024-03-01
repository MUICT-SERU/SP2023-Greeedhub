#!/usr/bin/python

from cloudInsightAPI import *
import getpass

def options():
	print "\r\n"
	print "======== MENU ========"
	print "1. List Environments"
	print "2. List Credentials"
	print "3. Create Credential"
	print "4. Create Environment"
	print "5. Delete Credential"
	print "6. Delete Environment"
	print "7. User Information"
	print "\r\n"
	opt = None
	while not opt:
		try:
			opt = int(raw_input("Select an option or 0 to exit: "))
			break
		except ValueError:
			print 'Enter a number'
	print "\r\n"
	return opt

def listSources(ciAPI):
	print "Listing Environments"
	for source in ciAPI.listSources("source.type=environment").itervalues(): #Listing the sources with a filter to environments
		print "Environment UUID: " + source.id
		print source
		print "===================================================================="

def listCredentials(ciAPI):
	print "Listing credentials"
	for lcredential in ciAPI.listCredentials().itervalues(): #Listing all the credentials of the user
		print "Credential UUID: " + lcredential.id
		print lcredential
		print "===================================================================="

def createCredential(ciAPI):
	print "Creating credential"
	arn = raw_input("Enter the ARN: ")
	external_id = raw_input("Enter the external id: ")
	credential_name = raw_input("Enter a credential name: ")
	type = "iam_role"
	dict_cred_data = { "arn" : arn, "external_id" : external_id }
	print ciAPI.createCredential(type, credential_name, dict_cred_data) #Creating a new credential

def createSource(ciAPI):
	print "Creating a source"
	credential = None
	while not credential:
		try:
			cred_uuid = raw_input("Enter the UUID of the credential: ")
			credential = ciAPI.credentials[cred_uuid]
		except KeyError:
			print "Invalid UUID"
	source_name = raw_input("Environment name: ")
	collection_type = "aws"
	scope = {}
	discover = bool(raw_input("Discover? Yes or empty for not: "))
	scan = bool(raw_input("Scan? Yes or empty for not: "))
	source = ciAPI.createSource(source_name, collection_type, credential, scope, discover, scan) #Creating an environment
	print source

loginAttempt = 0

def login(ciAPI):
	global loginAttempt
	loginAttempt += 1
	if loginAttempt == 5:
		print "Login Failed, program closed!"
		exit(1)
	print "System Login"
	print "Please Enter your login information"
	username = raw_input("Username: ")
	password = getpass.getpass("Password: ")
	success = ciAPI.login(username, password)
	return success

def main():
	#instance of the API object
	print "Welcome to the Cloud Insight API"
	ciAPI = CloudInsightAPI()
	success = False
	while not success:
		try:
			success = login(ciAPI)
		except requests.exceptions.RequestException as e:
			print e
	try:
		menu = options()
		while menu != 0:
			if menu == 1:
				try:
					listSources(ciAPI)
				except requests.exceptions.RequestException as e:
					print e
			elif menu == 2:
				try:
					listCredentials(ciAPI)
				except requests.exceptions.RequestException as e:
					print e
			elif menu == 3:
				try:
					createCredential(ciAPI)
				except requests.exceptions.RequestException as e:
					print e
			elif menu == 4:
				try:
					if len(ciAPI.credentials) == 0:
						listCredentials(ciAPI)
					createSource(ciAPI)
				except requests.exceptions.RequestException as e:
					print e
			elif menu == 5:
				try:
					if len(ciAPI.credentials) == 0:
						listCredentials(ciAPI)
					print "Deleting Credential"
					credential = None
					while not credential:
						try:
							cred_uuid = raw_input("Enter the UUID of the credential: ")
							credential = ciAPI.credentials[cred_uuid]
							ciAPI.deleteCredential(credential.id) #Deleting credential by ID
							del ciAPI.credentials[cred_uuid]
						except KeyError:
							print "Invalid UUID"
						except requests.exceptions.RequestException as e:
							print e
				except requests.exceptions.RequestException as e:
					print e
			elif menu == 6:
				try:
					if len(ciAPI.sources) == 0:
						listSources(ciAPI)
					print "Deleting Environment"
					source = None
					while not source:
						try:
							source_uuid = raw_input("Enter the UUID of the environment: ")
							source = ciAPI.sources[source_uuid]
							ciAPI.deleteSource(source.id) #Deleting source by ID
							del ciAPI.sources[source_uuid]
						except requests.exceptions.RequestException as e:
							print e
						except KeyError:
							print "Invalid UUID"
				except requests.exceptions.RequestException as e:
					print e
			elif menu == 7:
				print "TOKEN:"
				print ciAPI.token #Show temporary access token information
				print "User Information"
				print ciAPI.user #Show user information
			else:
				print "Invalid option"
			menu = options()
	except requests.exceptions.RequestException as e:
		print e

if __name__ == "__main__":
	main()
