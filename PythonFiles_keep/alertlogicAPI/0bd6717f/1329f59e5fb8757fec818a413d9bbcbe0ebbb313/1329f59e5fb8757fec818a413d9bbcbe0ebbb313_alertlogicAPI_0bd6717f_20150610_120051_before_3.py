#!/usr/bin/python

from alertLogicAPI import *

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
	opt = None
	while not opt:
		try:
			opt = int(raw_input("Select an option or 0 to exit: "))
			break
		except ValueError:
			print 'Enter a number'
	print "\r\n"
	return opt

loginAttempt = 0

def login(alAPI):
	global loginAttempt
	loginAttempt += 1
	if loginAttempt == 5:
		print "Login Failed, program closed!"
		exit(1)
	print "System Login"
	print "Please Enter your login information"
	username = raw_input("Username: ")
	password = raw_input("Password: ")
	try:
		success = alAPI.login(username, password)
		return success
	except requests.exceptions.RequestException as e:
		print e

def main():
	#instance of the API object
	print "Welcome to the Alert Logic API"
	alAPI = AlertLogicAPI()
	#username = "admin@ozone.com"
	#password = "1newP@ssword"
	success = False
	while not success:
		try:
			success = login(alAPI)
		except requests.exceptions.RequestException as e:
			print e
	try:
		menu = options()
		while menu != 0:
			if menu == 1:
				print "Listing Environments"
				for idx, source in enumerate(alAPI.listSources("source.type=environment")): #Listing the sources with a filter to environments
					print "Environment number " + str(idx)
					print source
			elif menu == 2:
				print "Listing credentials"
				for idx, lcredential in enumerate(alAPI.listCredentials()): #Listing all the credentials of the user
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
				credential = alAPI.createCredential(type, credential_name, dict_cred_data) #Creating a new credential
			elif menu == 4:
				if len(alAPI.credentials) == 0:
					print "Listing credentials"
					for idx, lcredential in enumerate(alAPI.listCredentials()):
						print "Credential number " + str(idx)
						print lcredential
				print "Creating a source"
				credential = None
				idx = None
				while not credential and not idx:
					try:
						idx = int(raw_input("Enter the number of the credential: "))
						try:
							if idx < 0:
								raise IndexError
							credential = alAPI.credentials[idx]
						except IndexError:
							print "Invalid number"
							idx = None
						except TypeError:
							print "Enter a number"
					except ValueError:
						print "Enter a number"
				source_name = raw_input("Source name: ")
				print "Collection Type: aws"
				collection_type = raw_input("Collection type: ")
				scope = {}
				discover = bool(raw_input("Discover? Yes or empty for not: "))
				scan = bool(raw_input("Scan? Yes or empty for not: "))
				try:
					source = alAPI.createSource(source_name, collection_type, credential, scope, discover, scan) #Creating an environment
					print source
				except requests.exceptions.RequestException as e:
					print e
			elif menu == 5:
				if len(alAPI.credentials) >= 1:
					print "Deleting Credential"
					idx = input("Enter the number of the credential: ")
					try:
						alAPI.deleteCredential(alAPI.credentials[idx].id) #Deleting credential by ID
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
						alAPI.deleteSource(alAPI.sources[idx].id) #Deleting source by ID
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
				print alAPI.token #Show temporary access token information
				print "User Information"
				print alAPI.user #Show user information
			else:
				print "Invalid option"
			menu = options()

	except requests.exceptions.RequestException as e:
		print e

if __name__ == "__main__":
	main()
