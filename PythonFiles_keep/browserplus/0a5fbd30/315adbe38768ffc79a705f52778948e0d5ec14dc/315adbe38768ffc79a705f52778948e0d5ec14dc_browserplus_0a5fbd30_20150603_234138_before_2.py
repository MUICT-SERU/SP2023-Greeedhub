#! /usr/bin/python

# NOTE: this is for creation of feeds to make courses *live*

# Edited by Vincent Au to allow multiple csv passing and universal newline
# character detection (you can use Excel to edit csv now)

import argparse
import csv
import os

YEAR = "2015"

DEPARTMENT_DICT = {
    "Crawford School of Public Policy" : "Crawford",
    "Digital Learning Project" : "DLP",
    "School of Culture, History &amp; Language" : "CHL",
    "Coral Bell School of Asia Pacific Affairs" : "Bell",
    "School of Regulation, Justice &amp; Diplomacy" : "RJD"
}

SHORT_NAME_DICT = {
    "Autumn" : "_Aut_" + YEAR,
    "Full year" : "_Year_" + YEAR,
    "Summer" : "_Sum_" + YEAR,
    "Semester 1" : "_Sem1_" + YEAR,
    "Semester 2" : "_Sem2_" + YEAR,
    "Spring" : "_Spr_" + YEAR,
    "Winter" : "_Win_" + YEAR
}

def process(inFile, append_name=True):
    outCourseName = "liveCourseFeed"
    outSectionName = "liveSectionFeed"

    name = os.path.basename(inFile.name)
    if append_name:
        outCourseName += name
        outSectionName += name
    else:
        outCourseName += ".csv"
        outSectionName += ".csv"

    outCourse = open(outCourseName,'wb+')
    outSection = open(outSectionName,'wb+')
    
    reader = csv.DictReader(inFile, delimiter=",", quotechar='"')
    courseWriter = csv.writer(outCourse, delimiter="|", quotechar='"')
    sectionWriter = csv.writer(outSection, delimiter="|", quotechar='"')

    courseWriter.writerow(["COURSE_IDENTIFIER", "TITLE", "CAMPUS_IDENTIFIER",
        "DEPARTMENT_IDENTIFIER", "START_DATE", "END_DATE",
        "CLONE_FROM_IDENTIFIER", "TIMEZONE", "PREFIX", "NUMBER", "INSTRUCTOR",
        "SESSION", "YEAR", "CREDITS", "DELIVERY_METHOD", "IS_STRUCTURED",
        "IS_TEMPLATE", "HIDDEN_FROM_SEARCH"
    ])

    sectionWriter.writerow(["COURSE_IDENTIFIER", "SECTION_IDENTIFIER",
        "SECTION_LABEL"])

    for row in reader:
        courseToWrite = []
        sectionToWrite = []
        
        courseToWrite.append(row["Course Identifier"].split("_")[0]
                + SHORT_NAME_DICT[row["Session"]])
        
        courseToWrite +=  [row["Title"], "Live",
                DEPARTMENT_DICT[row["Department"]], row["Start Date"],
                row["End Date"], row["Course Identifier"], "Australia/Sydney",
                row["Designation"].split("-")[0],
                row["Designation"].split("-")[1], row["Instructor"],
                row["Session"], row["Year"], row["Credits"],
                row["Delivery Method"], "1", "0", "0"
                ]
        
        sectionToWrite.append(courseToWrite[0])
        sectionToWrite += [sectionToWrite[0] + "_Final", "Final"]

        courseWriter.writerow(courseToWrite)
        sectionWriter.writerow(sectionToWrite)

    inFile.close()
    outCourse.close()
    outSection.close()
    
    print("Success! %s has been processed." % name)
    print("Check %s and %s for results." % (outCourseName, outSectionName))


def main(args):
    default_name = "report.csv"
    if len(args.files) < 1:
        print("No filenames provided. Defaulting to %s" % default_name)
        try:
            with open(default_name, "Urb") as f:
                process(f, False)
        except IOError:
            print("Error: %s not found" % default_name)
            return 1
    else:
        for f in args.files:
            process(f)
    return 0


parser = argparse.ArgumentParser(
        description="Turn draft csv into final course and section csv."
        )
parser.add_argument("files", type=argparse.FileType('Urb'), nargs='*',
        help='csv filenames')
main(parser.parse_args())
