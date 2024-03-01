import logging
import sys
import time
from browserplus import BrowserPlus
from getpass import getpass
from subprocess import Popen, PIPE
from urllib import quote_plus
from urlparse import urlparse, parse_qs, urljoin

# CONFIGURATION CONSTANTS
_SEARCH_STRING_DICT = {
    "AUT" : "Autumn",
    "YEAR" : "Full year",
    "SUM" : "Summer",
    "SEM1" : "Semester 1",
    "SEM2" : "Semester 2",
    "SPR" : "Spring",
    "WIN" : "Winter"
}

_CAMPUS_DICT = {
    "Unused_Draft" : 4,
    "Final" : 3,
    "Draft" : 2,
    "Any" : -1
}


_log = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

_browser = BrowserPlus()

class User(object):

    def __init__(self, uid, fname, lname, email=""):
        self.uid = uid
        self.firstname = fname
        self.lastname = lname
        if email:
            self.email = email
        else:
            self.email = _gen_email(fname, lname)

    def __str__(self):
        return "%s %s" % (self.firstname, self.lastname)


class UserFeed(object):

    def __init__(self):
        self.users = {}

    def _gen_filename(self):
        name = str("UserFeed%s.csv" % time.strftime("%Y%m%d-%H%M%S"))
        return name

    def generate(self, filename=""):
        if not filename:
            filename = self._gen_filename()
        feed = open(filename, "w")
        line = "USER_IDENTIFIER|FIRST_NAME|LAST_NAME|EMAIL|INTERNAL_USER\n"
        feed.write(line)
        for l in self.users.values():
            feed.write(l)
        feed.close()
        return filename

    def add_user(self, uid, first, last, email=""):
        if not email:
            email = _gen_email(first, last)
        line = "%s|%s|%s|%s|1\n" % (uid, first, last, email)
        self.users[uid] = line


class Course(object):

    def __init__(self, shortname):
        #shortname = "STST8002_Sem2_2015" #for example
        self.shortname = shortname
        self.name = shortname.split("_")[0]
        self.session = _SEARCH_STRING_DICT[shortname.split("_")[1].upper()]
        self.year = shortname.split("_")[2]

    def __str__(self):
        return self.name


class CourseFeed(object):

    def __init__(self):
        self.courses = {}

    def _gen_filename(self):
        name = str("CourseFeed%s.csv" % time.strftime("%Y%m%d-%H%M%S"))
        return name

    def generate(self, filename=""):
        if not filename:
            filename = self._gen_filename()
        feed = open(filename, "w")
        line = (
            "COURSE_IDENTIFIER|TITLE|CAMPUS_IDENTIFIER|DEPARTMENT_IDENTIFIER|"
            "START_DATE|END_DATE|CLONE_FROM_IDENTIFIER|TIMEZONE|PREFIX|NUMBER|"
            "INSTRUCTOR|SESSION|YEAR|CREDITS|DELIVERY_METHOD|IS_STRUCTURED|"
            "IS_TEMPLATE|HIDDEN_FROM_SEARCH\n"
            )
        feed.write(line)
        for l in self.courses.values():
            feed.write(l)
        feed.close()
        return filename

    def add_course(self, shortname, title, dept, template, convener="",
                   units="6", method="In Person"):
        c = Course(shortname)
        sy = c.year[-2:] #short year (last two digits of year)
        subject = c.name[:4]
        code = c.name[4:]
        string = (
            "%s_Draft|%s|DRAFT|%s|01/01/%s|12/01/%s|%s|Australia/Sydney|"
            "%s|%s|%s|%s|%s|%s|%s|1|1|0\n"
            )
        line = string % (
            c.name, title, dept, sy, sy, template, subject, code, convener,
            c.session, c.year, units, method
        )
        self.courses[shortname] = line


class SectionFeed(object):

    def __init__(self):
        self.courses = {}

    def _gen_filename(self):
        name = str("SectionFeed%s.csv" % time.strftime("%Y%m%d-%H%M%S"))
        return name

    def generate(self, filename=""):
        if not filename:
            filename = self._gen_filename()
        feed = open(filename, "w")
        line = "COURSE_IDENTIFIER|SECTION_IDENTIFIER|SECTION_LABEL\n"
        feed.write(line)
        for l in self.courses.values():
            feed.write(l)
        feed.close()
        return filename

    def add_course(self, shortname):
        c = Course(shortname)
        string = "%s_Draft|%s_Draft_Draft|Draft\n"
        line = string % (c.name, c.name)
        self.courses[shortname] = line


def _gen_email(firstname, lastname):
    """Email rules depending on their name.
    simple: Firstname Lastname => firstname.lastname@anu.edu.au
    apostrophes: e.g. Bina D'Cost => bina.dcosta@anu.edu.au
    complex: (de, le) => ???
    """
    first = firstname.lower()
    last = lastname.lower()
    #simple
    if first.isalpha() and last.isalpha():
        return "%s.%s@anu.edu.au" % (first, last)

    #apostrophes
    first = first.replace("'", "")
    last = last.replace("'", "")
    return "%s.%s@anu.edu.au" % (first, last)


def _validCoursename(course):
    return course[:4].isalpha() and course[4:8].isdigit()

def _validShortname(short):
    return short.count('_') >= 2 and _validCoursename(short.split('_')[0])

def _gen_search_url(name, section="Any", session="", year=""):
    subject = name[:4]
    code = name[4:]
    searchString = ("https://anu.campusconcourse.com/search?search_performed=1"
                    "&sort_by=year&descend=true")
    searchString += "&prefix=" + subject
    searchString += "&number=" + code
    searchString += "&campus_id=" + str(_CAMPUS_DICT[section])
    searchString += "&year=" + year
    searchString += "&session=" + quote_plus(session)
    return searchString

def _is_logged_in():
    #wrapped in try block since this can be called before a page load
    try:
        menu = _browser.find('nav#l1-nav ul.navbar-right')
        return "Login" not in menu.xpath('string()')
    except:
        return False

def _login():
    username = raw_input("Enter your Concourse email: ")
    password = getpass("Enter your Concourse password: ")
    _browser.open("https://anu.campusconcourse.com/login")

    _browser.select_form_by("action", "login")
    _browser["email"] = username
    _browser["password"] = password
    _browser.submit()
    errormsg = "The information you provided does not match our records"
    return not _browser.has(errormsg)

def _require_login():
    while not _is_logged_in():
        if not _login():
            _log.error("Incorrect details. Please try again.")

def is_valid(text):
    return _validShortname(text) or _validCoursename(text)

def is_valid_uid(username):
    return len(username) > 0 and username[0] == 'u' and username[1:].isdigit()

def get_user(unumber):
    if not is_valid_uid(unumber):
        _log.error("%s is not a valid unumber", unumber)
        return None

    _require_login()

    page = "https://anu.campusconcourse.com/admin_users?keyword=" + unumber
    _browser.open(page)
    errormsg = "No users found. Please try again."
    if _browser.has(errormsg):
        return None

    table = _browser.find('div.table-responsive')
    firstname = table.cssselect('td')[0].text
    lastname = table.cssselect('td')[1].text
    return User(unumber, firstname, lastname)


def find_course(shortname, exact=True, section="Any"):
    url = ""
    if _validShortname(shortname):
        course = Course(shortname)
        if exact:
            url = _gen_search_url(course.name, section, course.session, course.year)
        else:
            url = _gen_search_url(course.name, section)
    elif _validCoursename(shortname):
        url = _gen_search_url(shortname, section)
    else:
        return False
    _browser.open(url)
    errormsg = 'No results found.'
    return not _browser.has(errormsg)

def get_course_url(name, exact=True, section="Any"):
    if not find_course(name, exact, section):
        return ""
    table = _browser.find('#results_table')
    return urljoin(_browser.geturl(), table.find('.//a').attrib['href'])

def get_course_id(shortname, exact=True, section="Any"):
    site = get_course_url(shortname, exact, section)
    if not site:
        return ""
    return parse_qs(urlparse(site).query)['course_id'][0]

def _get_permission_code(name):
    e = _browser.find('#groups').xpath('.//option[text()="%s"]' % name)
    if len(e) > 0:
        return e[0].get('value')
    return None

def set_lecturer(shortname, uid, group):
    courseid = get_course_id(shortname, True, "Draft")
    if not courseid or not _validShortname(shortname):
        _log.error("Cannot find %s", shortname)
        return False

    user = get_user(uid)
    if not user:
        _log.error("%s is not in the concourse user database", uid)
        return False

    #check and see if the user is there
    _require_login()
    page = "https://anu.campusconcourse.com/manage_users"
    query = "?course_id=" + courseid
    _browser.open(page + query)

    if _browser.has("%s, %s" % (user.lastname, user.firstname)):
        _log.debug('%s is already teaching %s', user.firstname, shortname)
        return False

    code = _get_permission_code(group)
    if not code:
        _log.error("Can't find group: %s", group)
        return False

    #fix the info
    _browser.select_form_by("action", "add_users")
    _browser["emails"] = user.email
    _browser["group_id"] = [code]
    _browser.submit()

    errormsg = "No new users were added to the course."
    return not _browser.has(errormsg)

def transform_course(shortname):
    """This will find a draft version of an existing course and transform it to
    to fit the course shortname. e.g. if INTR8018_Sem2_2014 exists but not
    INTR8018_Sem2_2015 then it will ammend the date and start/end dates to be 2015.
    """
    courseid = get_course_id(shortname, False, "Draft")
    if not courseid:
        return False

    #change course info
    _require_login()
    page1 = "https://anu.campusconcourse.com/change_course_settings"
    query = "?course_id=" + courseid
    _browser.open(page1 + query)

    #fix the info
    search = "edit_course_information" + query
    _browser.select_form_by("action", search)
    course = Course(shortname)
    _browser["session"] = [course.session]
    _browser["year"] = [course.year]
    _browser.submit()

    #check if okay
    msg = "Course info has been updated!"
    if not _browser.has(msg):
        _log.error("Error occured while attempting to change %s settings",
                   course.name)
        return False

    #change required course info
    page2 = "https://anu.campusconcourse.com/edit_required_course_information"
    _browser.open(page2 + query)

    search = "edit_required_course_information" + query
    _browser.select_form_by("action", search)

    #fix the info
    _browser["campus_id"] = [str(_CAMPUS_DICT["Draft"])]
    _browser["start_date"] = course.year + "-01-01"
    _browser["end_date"] = course.year + "-12-01"
    _browser.submit()

    msg = "Required course information has been updated!"
    return _browser.has(msg)

def _get_secret_key():
    _require_login()
    _browser.open('https://anu.campusconcourse.com/admin_process_feed')
    return _browser.find('#shared_secret').get('value')

def process_feed(feedtype, filename):
    url = "https://anu.campusconcourse.com/process_feed_file"
    secret = _get_secret_key()

    #HMAC=`cat $FILENAME | openssl dgst -sha256 -hmac $SECRET | cut -d' ' -f2`
    p1 = Popen(['cat', filename], stdout=PIPE)
    p2 = Popen(['openssl', 'dgst', '-sha256', '-hmac', secret],
               stdin=p1.stdout, stdout=PIPE)
    p1.stdout.close()
    p3 = Popen(['cut', '-d', ' ', '-f2'], stdin=p2.stdout,
               stdout=PIPE)
    p2.stdout.close()
    hmac = p3.communicate()[0].strip()

    #curl --tlsv1 -F type=$TYPE -F hmac=$HMAC -F file=@$FILENAME $URL
    cmd = 'curl --tlsv1 -F type=%s -F hmac=%s -F file=@%s %s' % (
        feedtype, hmac, filename, url
    )
    p4 = Popen(cmd.split(' '), stdout=PIPE, stderr=PIPE)
    out, _ = p4.communicate()
    exitcode = p4.returncode
    print(out)
    return exitcode


