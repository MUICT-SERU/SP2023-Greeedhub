# Copyright (C) 2014 Adam Schubert <adam.schubert@sg1-game.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

__author__="Adam Schubert <adam.schubert@sg1-game.net>"
__date__ ="$6.10.2014 5:09:42$"



from dwa.Requester import Requester
from dwa.TypeLayer import TypeLayer

DEFAULT_BASE_URL = "http://api.divine-warfare.com"
DEFAULT_VERSION = 1.0
DEFAULT_TIMEOUT = 10

class Dwa(object):

  def __init__(self, apiToken=None, baseUrl=DEFAULT_BASE_URL, timeout=DEFAULT_TIMEOUT, version=DEFAULT_VERSION, userAgent='DwaPython'):
    self.requester = Requester(apiToken, baseUrl, timeout, version, userAgent)
    
  def __getattr__(self, name):
    return TypeLayer(name)
    
    
  def get_users(self):
    #headers, data = self.__requester.request_json_check('GET', '/users/list/{api_token}/{server}/{limit}/{page}', {'server': 1, 'limit': 20, 'page': 0})
        
    #print (headers)
    #print (data)
    print (self.requester.requestJsonCheck('GET', '/user/list/{api_token}/{limit}/{page}', { 'limit': 20, 'page': 0})[1])
    #print (self.requester.requestMultipartAndCheck('POST', '/user/create/{api_token}', {''}))
    #print (self.requester.requestJsonCheck('POST', '/user/create/{api_token}', {}, { 'username': 'Apitest', 'password': 'apitest'})[1])