"""
   This sample shows how to loop through all users
   and delete all their content and groups

"""

import arcrest
from arcresthelper import resettools
def trace():
    """
        trace finds the line, the filename
        and error message and returns it
        to the user
    """
    import traceback, inspect
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]
    filename = inspect.getfile(inspect.currentframe())
    # script name + line number
    line = tbinfo.split(", ")[1]
    # Get Python syntax error
    #
    synerror = traceback.format_exc().splitlines()[-1]
    return line, filename, synerror

def main():
    proxy_port = None
    proxy_url = None    

    securityInfo = {}
    securityInfo['security_type'] = 'Portal'#LDAP, NTLM, OAuth, Portal, PKI
    securityInfo['username'] = "<UserName>"
    securityInfo['password'] = "<Password>"
    securityInfo['org_url'] = "http://www.arcgis.com"
    securityInfo['proxy_url'] = proxy_url
    securityInfo['proxy_port'] = proxy_port
    securityInfo['referer_url'] = None
    securityInfo['token_url'] = None
    securityInfo['certificatefile'] = None
    securityInfo['keyfile'] = None
    securityInfo['client_id'] = None
    securityInfo['secret_id'] = None   

    try:
        
        rst = resettools.resetTools(securityinfo=securityInfo)
        if rst.valid:
            users = {'users':[{'username':securityInfo['username']}]}
            #arh.removeUserData(users=users)
            #arh.removeUserGroups(users=users
            rst.removeUserData(users=users)
            rst.removeUserGroups(users=users) 
        else:
            print rst.message
    except:
        line, filename, synerror = trace()
        print("error on line: %s" % line)
        print("error in file name: %s" % filename)
        print("with error message: %s" % synerror)

if __name__ == "__main__":
    main()