#! /usr/bin/python

# Returns the user from a wattle number
# Vincent Au (c) 2015

import argparse
import getpass
import logging
import os
import re
import sys
import xlrd
from BeautifulSoup import BeautifulSoup
from mechanize import Browser
from urllib import quote_plus
from urlparse import urlparse

log = logging.getLogger()
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

def exists(soup, msg):
    return soup.find(text=re.compile(msg)) != None

def genSearchString(userid):
    searchString = ("http://wattlecourses.anu.edu.au/enrol/users.php?id=5373"
            "&search=" + userid)
    return searchString

class User(object):

    def __init__(self, userid, name):
        self.userid = userid
        self.name = name

    def __str__(self):
        return self.name

class UserFinder(object):

    def __init__(self, browser):
        self.browser = browser

    def getUser(self, userid):
        b = self.browser
        b.open(genSearchString(userid))

        soup = BeautifulSoup(b.response().read())
        searchResults = soup.find('tr', 'userinforow')
        
        if searchResults == None:
            return None
        else:
            return searchResults.find('div', 'subfield_firstname').text

def login(b, page):
    username = raw_input("Please enter your Wattle ID: ")
    password = getpass.getpass("Please enter your Wattle password: ")
    b.open(page)

    # logging in
    formcount = 0
    for frm in b.forms():
        if str(frm.attrs["id"])=="login":
            break
        formcount += 1
    b.select_form(nr=formcount)
    b["username"] = username
    b["password"] = password
    b.submit()
    soup = BeautifulSoup(b.response().read())
    errormsg = "Invalid login, please try again"
    return not exists(soup, errormsg)

def main(args):
    b = Browser()
    b.set_handle_robots(False)
    b.addheaders = [('Accept',
        'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')]

    page = "https://wattlecourses.anu.edu.au/login/index.php"
    if login(b, page):
        log.info("Logged in successfully.")
    else:
        log.error("Login failed. Check your login details before trying again")
        return 1

    log.disabled = not args.log

    finder = UserFinder(b)

    userid = raw_input("ID to search: ")
    user = finder.getUser(userid)
    if user != None:
        print(user)
    return 0
    
    if len(args.files) < 1:
        finder.process("")
    else:
        for f in args.files:
            finder.process(f)
    return 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description="See if courses exist on concourse."
            )
    parser.add_argument("files", nargs='*', help='filenames')
    parser.add_argument('-l', '--log', action='store_true', default=False)
    parser.add_argument('-c', '--create', action='store_true', default=False)
    main(parser.parse_args())
