from . import UserData

import os
import sys


OPT_SUBTYPE_MAP={
    "":                              None,
    "auto":                          None,
    "cb":                            "cloud-boothook",
    "cloud-boothook":                "cloud-boothook",
    "cc":                            "cloud-config",
    "cloud-config":                  "cloud-config",
    "ca":                            "cloud-config-archive",
    "cloud-config-archive":          "cloud-config-archive",
    "ph":                            "part-handler",
    "part-handler":                  "part-handler",
    "uj":                            "upstart-job",
    "upstart-job":                   "upstart-job",
    "io":                            "x-include-once-url",
    "include-once":                  "x-include-once-url",
    "x-include-once-url":            "x-include-once-url",
    "in":                            "x-include-url",
    "include":                       "x-include-url",
    "x-include-url":                 "x-include-url",
    "sh":                            "x-shellscript",
    "shellscript":                   "x-shellscript",
    "x-shellscript":                 "x-shellscript",
}


def print_error(message):
    print("{0}: {1}".format("mkciud", message), file=sys.stderr)


def print_usage():
    print("usage: {0} [ [type-specifier:]filename ]+".format("mkciud"), file=sys.stderr)

def print_type_specifiers():
    print("type-specifiers:",                                                   file=sys.stderr)
    print("    (default), (empty string), auto           autodetect",           file=sys.stderr)
    print("    cb, cloud-boothook                        cloud-boothook",       file=sys.stderr)
    print("    cc, cloud-config                          cloud-config",         file=sys.stderr)
    print("    ca, cloud-config-archive                  cloud-config-archive", file=sys.stderr)
    print("    ph, part-handler                          part-handler",         file=sys.stderr)
    print("    uj, upstart-job                           upstart-job",          file=sys.stderr)
    print("    io, include-once, x-include-once-url      x-include-once-url",   file=sys.stderr)
    print("    in, include, x-include-url                x-include-url",        file=sys.stderr)
    print("    sh, shellscript, x-shellscript            x-shellscript",        file=sys.stderr)


def main(args=None):
    if args is None:
        args = sys.argv

    try:
        
        args = args[1:]

        if len(args) == 0:
            print_usage()
            return os.EX_USAGE

        userdata = UserData()
        for arg in args:
            sep = arg.find(":")
            if sep != -1:
                ts = arg[:sep]
                fn = arg[sep+1:]
            else:
                ts = ""
                fn = arg
            if ts not in OPT_SUBTYPE_MAP:
                print_error("Invalid type specifier: \"{}\"".format(ts))
                print_type_specifiers()
                return os.EX_USAGE
            message_subtype = OPT_SUBTYPE_MAP[ts]
            with open(fn, "r") as f:
                message_body = f.read()
            userdata.add(message_body, message_subtype)
        userdata.export(sys.stdout.buffer)
        return os.EX_OK

    except Exception as e:
        print_error(str(e))
        return os.EX_SOFTWARE


if __name__ == "__main__":
    sys.exit(main(sys.argv))
