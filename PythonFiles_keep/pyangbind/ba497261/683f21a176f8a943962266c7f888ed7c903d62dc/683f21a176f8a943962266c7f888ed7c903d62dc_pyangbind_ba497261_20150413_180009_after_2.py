"""Generate YANG Python Bindings from a YANG model.

(c) Rob Shakir (rob.shakir@bt.com, rjs@rob.sh) - 2015.

This module is tentatively licensed under the Apache licence.

"""

import optparse
import sys
import re
import string

from pyang import plugin
from pyang import statements

USED_TYPES = []

#class YANGParent():
#  name = str()
#  def __init__(self, n):
#    self.name = n
#
#class YANGContainer(YANGParent):
#  pass

# this is a hack solution, we need to fix this to have
# dynamic learning of types

class_bool_map = {
  'false':  False,
  'False':  False,
  'true':    True,
  'True':    True,
}

class_map = {
  'boolean':        ("YANGBool", class_bool_map),
  'uint8':        ("np.uint8", False),
  'uint16':        ("np.uint16", False),
  'uint32':        ("np.uint32", False),
  'string':        ("str", False),
  # we need to look at how to parse typedefs
  'inet:as-number':     ("int", False),
  'inet:ipv4-address':   ("str", False),
  'decimal64':       ("float", False),
  # more types to be added here
}

def safe_name(arg):
  """
    Make a leaf or container name safe for use in Python.
  """
  arg = arg.replace("-", "_")
  return arg

def pyang_plugin_init():
    plugin.register_plugin(BTPyClass())

class BTPyClass(plugin.PyangPlugin):
    def add_output_format(self, fmts):
        self.multiple_modules = True
        fmts['bt'] = self

    def emit(self, ctx, modules, fd):
        build_btclass(ctx, modules, fd)


def build_btclass(ctx, modules, fd):
  # numpy provides some elements of the classes datatypes
  fd.write("from operator import attrgetter\n")
  fd.write("import numpy as np\n\n")

  fd.write("""import collections

# using solution from
# http://stackoverflow.com/questions/3487434/overriding-append-method\
# -after-inheriting-from-a-python-list
# to create a list type that can be restricted to a certain type - to support\
# leaf-list.
class TypedList(collections.MutableSequence):
  def __init__(self, allowed_types, *args):
    self.allowed_types = type
    self.list = list()
    self.extend(list(args))

  def check(self, v):
    if not isinstance(self, allowed_types):
      raise TypeError, v

  def __len__(self): return len(self.list)

  def __getitem__(self,i): return self.list[i]

  def __delitem__(self,i): del self.list[i]

  def __setitem__(self, i, v):
    self.check(v)
    self.list[i] = v

  def insert(self, i, v):
    self.check(v)
    self.list.insert(i,v)

  def __str__(self):
    return str(self.list)

class YANGBool(int):
  __v = 0
  def __init__(self,v=False):
    if v in [0, False, "false", "False"]:
      self.__v = 0
    else:
      self.__v = 1
  def __repr__(self):
    return str(True if self.__v else False)

def defineYANGDynClass(*args, **kwargs):
  base_type = kwargs.pop("base",int)
  class YANGDynClass(base_type):
    _changed = False
    _default = False

    def yang_set(self):
      return self._changed

    def __repr__(self):
      #print self._default
      ####
      #
      # if a variable is not set in YANG, then if we print it, it should
      # still show the default value.
      # but, when doing a comparison, then it should not be equal (it should)
      # rather be equal to the unset value
      #
      ###
      if self._default and not self._changed:
        return repr(self._default)
      else:
        return super(YANGDynClass, self).__repr__()

    def __str__(self):
      return self.__repr__()

    def __init__(self, *args, **kwargs):
      #print "__init__ was called with %s and %s" % (args, kwargs)
      pass

    def __new__(self, *args, **kwargs):
      #print "__new__ was called with %s and %s" % (args, kwargs)
      default = kwargs.pop("default", None)
      try:
        value = args[0]
      except IndexError:
        value = None

      #print "args: %s, kwargs: %s" % (args,kwargs)
      obj = base_type.__new__(self, *args, **kwargs)
      if default == None:
        if value == None or value == base_type():
          # there was no default, and the value was not set, or was
          # set to the default of the base type
          obj._changed = False
        else:
          # there was no default, and the value was something other
          # than a default - the object has changed
          obj._changed = True
      else:
        # there is a default - if the value is not the same as that default
        # then we have changed the object.
        if value == None:
          # if the value is none, then we have not changed it
          obj._changed = False
        elif not value == default:
          obj._changed = True
        else:
          obj._changed = False

      obj._default = default
      return obj

  return YANGDynClass(*args,**kwargs)
""")

  # we need to parse each module
  for module in modules:
    # we need to parse each sub-module
    mods = [module]
    for i in module.search('include'):
      subm = crx.get_module(i.arg)
      if subm is not None:
        mods.append(subm)

    for m in mods:
      children = [ch for ch in module.i_children
            if ch.keyword in statements.data_definition_keywords]


      get_children(fd, children, m, m)



def get_children(fd, i_children, module, parent, path=str()):
  used_types,elements = [],[]
  for ch in i_children:
    elements += get_element(fd, ch, module, parent, path+"/"+ch.arg)

  #for element in elements:
    #print element
  #  if element["class"] == "leaf" and not element["type"] in used_types:
  #    used_types.append(element["type"])

  if not path == "":
    fd.write("class yc_%s_%s(object):\n" % (parent.arg, path.replace("/", "_")))
  else:
    fd.write("class %s(object):\n" % parent.arg)
  fd.write("""  \"\"\"
   This class was auto-generated by the PythonClass plugin for PYANG
   from YANG module %s - based on the path %s.
   Each member element of the container is represented as a class
   variable - with a specific YANG type.
  \"\"\"\n"""  % (module.arg, (path if not path == "" else "/")))

  #elem_getter_required = []
  if len(elements) == 0:
    fd.write("  pass\n")
  else:
    for i in elements:
      if type(i["type"]) == type((1,1)):
        fd.write("  __%s = %s(%s)\n" % (i["name"],
                                        i["type"][0], i["type"][1]))
      else:
        #fd.write("  %s%s = %s(%s)\n" % ("__" if i["config"] else "", i["name"],
        #                                  i["type"], i["default"] if "default" \
        #                                  in i.keys() and not i["default"] == \
        #                                  None else ""))
        class_str = "  __%s" % (i["name"])
        class_str += " = defineYANGDynClass("
        class_str += "base=%s" % i["type"]
        class_str += "%s)\n" % (", default=%s" % (i["default"]) if "default" in \
                              i.keys() and not i["default"] == None else "")
        fd.write(class_str)
      #if i["config"] == False:
      #  elem_getter_required.append(i["name"])

  #for e in elem_getter_required:
  #  fd.write("""  %s = property(attrgetter("%s"))\n""" % (re.sub("^_","",i["name"]), i["name"]))
    node = {}
    for i in elements:
      fd.write("""
  def _get_%s(self):
    \"\"\"
      Getter method for %s, mapped from YANG variable %s (%s)
    \"\"\"
    return self.__%s
      """ % (i["name"], i["name"], i["path"], i["origtype"],
             i["name"]))
      if type(i["type"]) == type((1,1)):
        ntype = i["type"][0]
      else:
        ntype = i["type"]
      fd.write("""
  def _set_%s(self,v):
    \"\"\"
      Setter method for %s, mapped from YANG variable %s (%s)
      If this variable is read-only (config: false) in the
      source YANG file, then _set_%s is considered as a private
      method. Backends looking to populate this variable should
      do so via calling thisObj._set_%s() directly.
    \"\"\"
    try:
      t = defineYANGDynClass(v,base=%s)
    except (TypeError, ValueError):
      raise TypeError("%s must be of a type compatible with %s")
    self.__%s = t\n""" % (i["name"], i["name"], i["path"],
                          i["origtype"], i["name"], i["name"], \
                          ntype, i["name"], ntype, i["name"]))
    fd.write("\n")
    for i in elements:
      if i["config"]:
        fd.write("""  %s = property(_get_%s, _set_%s)\n""" % \
                          (i["name"], i["name"], i["name"]))
      else:
        fd.write("""  %s = property(_get_%s)\n""" % (i["name"], i["name"]))

  fd.write("\n")
  return True

def get_element(fd, element, module, parent, path):
  this_object = []
  default = False
  p = False
  create_list = False
  if hasattr(element, 'i_children'):
    #print element.keyword
    #print element.keyword
    if element.keyword in ["container", "list"]:
      p = True
    elif element.keyword in ["leaf-list"]:
      create_list = True
    if element.i_children:
      #print dir(element)
      #print "children of %s (%s)" % (element.arg,type(element.i_children))
      #for i in element.i_children:
      #  print "  %s" % i.arg
      chs = element.i_children
      #print "class yc_%s(YANGContainer):" % element.arg
      get_children(fd, chs, module, element, path)
      #print child_code
      this_object.append({"name": element.arg, "origtype": element.keyword,
                          "type": "yc_%s_%s" % (element.arg,
                          path.replace("/", "_")), "class": "container",
                          "path": path, "config": True})
      p = True
  if not p:
    #print dir(element)
    elemtype = class_map[element.search_one('type').arg]
    elemdefault = element.search_one('default').arg if \
                                        element.search_one('default') else None
    # This maps a 'default' specified in the YANG file to a to a default of the
    # Python type specified
    if elemtype[1] and elemdefault:
      elemdefault = elemtype[1][elemdefault]
    elemconfig = class_bool_map[element.search_one('config').arg] if \
                                  element.search_one('config') else True

    elemname = safe_name(element.arg)
    #print "Appending %s" % element.arg
    if create_list:
      elemtype = ("TypedList", elemtype[0])
    else:
      elemtype = elemtype[0]
    this_object.append({"name": elemname, "type": elemtype,
                        "origtype": element.search_one('type').arg, "path": path,
                        "class": "leaf", "default": elemdefault,
                        "config": elemconfig})
  return this_object

