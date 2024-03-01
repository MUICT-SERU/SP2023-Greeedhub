# coding=utf-8
"""
Profiler utility for python


Erik de Jonge
erik@a8.nl
license: gpl2
"""
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from pyprofiler import graph_profile_program


def main():
    """
    main
    """
    graph_profile_program("main_graph.py")


if __name__ == "__main__":
    main()
