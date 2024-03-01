# -*- coding: utf-8 -*-
#
# Copyright © 2009 Pierre Raybaut
# Licensed under the terms of the MIT License
# (see formlayout.py for details)

"""
Simple formlayout example

Please take a look at formlayout.py for more examples
(at the end of the script, after the 'if __name__ == "__main__":' line)
"""

import datetime
from formlayout import fedit

def create_datalist_example(json=False):
    test = [('str *', 'this is a string'),
            ('str_m *', """this is a 
             MULTILINE
             string"""),
            ('file *', 'file'),
            ('list *', [0, '1', '3', '4']),
            ('tuple *', (0, '1', '3', '4')),
            ('list2', ['--', ('none', 'None'), ('--', 'Dashed'),
                       ('-.', 'DashDot'), ('-', 'Solid'),
                       ('steps', 'Steps'), (':', 'Dotted')]),
            ('float', 1.2),
            (None, [('fi&rst', first_function), ('s&econd', second_function)]),
            (None, 'Other:'),
            ('int', 12),
            ('font', ('Arial', 10, False, True)),
            ('color', '#123409'),
            ('bool', True),
            ]
    if not json:
        # Adding data types which are *not* supported by json serialization
        test += [
                 ('date', datetime.date(2010, 10, 10)),
                 ('datetime', datetime.datetime(2010, 10, 10)),
                 ]
    return test
    
def create_datagroup_example(json=False):
    datalist = create_datalist_example(json=json)
    return ((datalist, "Category 1", "Category 1 comment"),
            (datalist, "Category 2", "Category 2 comment"),
            (datalist, "Category 3", "Category 3 comment"))

def apply_function(result):
    print(result)

def first_function():
    print('first')

def second_function():
    print('second')

#--------- datalist example
datalist = create_datalist_example()
print("result:", fedit(datalist, title="Example",
                       comment="This is just an <b>example</b>.",
                       apply=('Custom &Apply button', apply_function),
                       ok='Custom &OK button',
                       cancel='Custom &Cancel button',
                       result='dict'))

#--------- datagroup example
datagroup = create_datagroup_example(json=True)
print("result:", fedit(datagroup, "Global title", result='JSON'))

#--------- datagroup inside a datagroup example
datalist = create_datalist_example()
datagroup = create_datagroup_example()
print("result:", fedit(((datagroup, "Title 1", "Tab 1 comment"),
                        (datalist, "Title 2", "Tab 2 comment"),
                        (datalist, "Title 3", "Tab 3 comment")),
                        "Global title", result='XML'))
