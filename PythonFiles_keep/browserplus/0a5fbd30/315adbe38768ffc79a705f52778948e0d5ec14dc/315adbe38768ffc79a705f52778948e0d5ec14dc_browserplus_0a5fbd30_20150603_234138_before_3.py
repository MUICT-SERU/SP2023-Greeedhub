#! /usr/bin/python

import argparse
import concourse
import logging
import os
import sys
import xlrd

# CONFIGURATION CONSTANTS

EXCEL = [".xls", ".xlsx"]

DEFAULT = "courses.xls"

outputFound = "found.txt"
outputNotFound = "notfound.txt"
log = logging.getLogger()
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

class CourseFinder(object):

    def __init__(self):
        self.generate = False
        self.exact = True
       
    def setAutoGenerate(self, enabled):
        self.generate = enabled

    def setMatchExact(self, exact):
        self.exact = exact

    def process_course(self, shortname, found, notfound):
        if concourse.find_course(shortname, self.exact):
            found.write(shortname + "\n")
            log.debug("%s found" % shortname)
        else:
            log.debug("%s not found" % shortname)
            if self.exact and self.generate:
                log.debug("attempting to generate course for %s" % shortname)
                if concourse.transform_course(shortname):
                    found.write(shortname + "\n")
                    log.debug("%s generated" % shortname)
                    return
                else:
                    log.debug("%s failed to be generated" % shortname)
            notfound.write(shortname + "\n")

    def parse_text(self, filename, found, notfound):
        with open(filename) as f:
            for line in f:
                if concourse.is_valid(line.strip()):
                    self.process_course(line.strip(), found, notfound)

    def parse_excel(self, filename, found, notfound):
        book = xlrd.open_workbook(filename)
        sheet = book.sheet_by_index(0)
        for row in range(sheet.nrows):
            coursename = sheet.cell(row, 0).value
            if concourse.is_valid(coursename):
                course = Course(coursename)
                self.process_course(course, found, notfound)

    def parse_stdin(self, found, notfound):
        line = sys.stdin.readline().strip()
        while len(line) > 0:
            if concourse.is_valid(line):
                self.process_course(line, found, notfound)
            line = sys.stdin.readline().strip()

    def process(self, filename):
        found = open(outputFound, "w")
        notfound = open(outputNotFound, "w")
        if not filename:
            self.parse_stdin(found, notfound)
        else:
            name, extension = os.path.splitext(filename)
            if extension.lower() in EXCEL:
                self.parse_excel(filename, found, notfound)
            else: #interpret as text file per line
                self.parse_text(filename, found, notfound)
        found.close()
        notfound.close()
        log.debug("Results saved to %s and %s" % (outputFound, outputNotFound))

def main(args):
    log.disabled = not args.log

    finder = CourseFinder()
    finder.setAutoGenerate(args.create)
    finder.setMatchExact(not args.fuzzy)

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
    parser.add_argument('-c', '--create', action='store_true', default=False)
    parser.add_argument('-f', '--fuzzy', action='store_true', default=False)
    parser.add_argument('-l', '--log', action='store_true', default=False)
    main(parser.parse_args())
