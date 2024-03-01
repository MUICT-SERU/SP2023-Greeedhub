#!/usr/bin/python
import alertLogicAPI

def main():
	username = "admin@ozone.com"
	password = "1newP@ssword"
	print "Logging in the system"
	alAPI = AlertLogicAPI(username, password)

	#"""
	print "TOKEN:"
	print alAPI.token
	print alAPI.user
	#"""
	"""
	print "listing sources"
	for idx, source in enumerate(alAPI.listSources("source.type=environment")):
		print "Source number " + str(idx)
		print source
	"""
	"""
	print "Getting Source"
	source = alAPI.getSource("DA886339-EE02-4A3F-A9D5-0D39DD20AF7A")
	print source
	"""
	"""
	print "Deleting Source"
	alAPI.deleteSource("DA886339-EE02-4A3F-A9D5-0D39DD20AF7A")
	"""
	"""
	print "listing sources"
	for idx, source in enumerate(alAPI.listSources("source.type=environment")):
		print "Source number " + str(idx)
		print source
	"""
	"""
	print "Creating credential"
	type = "iam_role"
	arn = "arn:aws:iam::948063967832:role/Barry-Product-Integration"
	external_id = "67013024"
	credential_name = "Testing Obj"
	dict_cred_data = { "arn" : arn, "external_id" : external_id }
	credential = alAPI.createCredential(type, credential_name, dict_cred_data)
	print credential
	"""
	"""
	print "listing credentials"
	for idx, lcredential in enumerate(alAPI.listCredentials()):
		print "Credential number " + str(idx)
		print lcredential
	"""

	"""
	print "Getting credential"
	credential = alAPI.getCredential("7E630D12-8C5A-4FCB-BB04-459C26A31377")
	print credential
	"""
	"""
	print "Deleting Credential"
	alAPI.deleteCredential("7E630D12-8C5A-4FCB-BB04-459C26A31377")
	"""
	"""
	print "Creating a source"
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
		source_name = "Fabio-Enviroment-Test"
		collection_type = "aws"
		#scope = {"include": [{"type": "vpc","key": "/aws/us-east-1/vpc/vpc-1234"}]}
		scope = {}
		discover = False
		scan = False
		source = alAPI.createSource(source_name, collection_type, credential, scope, discover, scan)
		print source
	else:
		print "You must created or select a credential first"
	"""

if __name__ == "__main__":
	main()
