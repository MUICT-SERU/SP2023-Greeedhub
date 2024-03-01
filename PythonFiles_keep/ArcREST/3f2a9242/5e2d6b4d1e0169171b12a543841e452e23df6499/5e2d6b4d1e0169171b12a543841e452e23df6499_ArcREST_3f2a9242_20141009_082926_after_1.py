from ..security.security import OAuthSecurityHandler, AGOLTokenSecurityHandler
from .._abstract.abstract import BaseAGOLClass
from parameters import ItemParameter, BaseParameters
import urllib
import urlparse
import json
import os

########################################################################
class Content(BaseAGOLClass):
    """
    The Portal Content Root operation consists of items, user and group
    content, and feature operations. All resources and operations (other
    than publicly accessible items) under this URI require an authenticated
    user.
    """
    _baseURL = None
    _url = None
    _securityHandler = None
    _proxy_port = None
    _proxy_url = None
    #----------------------------------------------------------------------
    def __init__(self, url, securityHandler,
                 proxy_url=None,
                 proxy_port=None):
        """Constructor"""
        if url.lower().find("/content") < 0:
            self._url = url + "/content"
        else:
            self._url = url
        self._securityHandler = securityHandler
        self._proxy_port = proxy_port
        self._proxy_url = proxy_url
    #----------------------------------------------------------------------
    @property
    def contentRoot(self):
        """ returns the content root """
        return self._url
    #----------------------------------------------------------------------
    @property
    def featureContent(self):
        """ returns an instance of the feature class """
        return FeatureContent(url=self._url + "/features",
                              securityHandler=self._securityHandler,
                              proxy_url=self._proxy_url,
                              proxy_port=self._proxy_port)

    #----------------------------------------------------------------------
    def getUserContent(self, username):
        """
        The user's content are items either in the home folder for the user
        e.g. /content/users/<username>, or in a subfolder of the home
        folder with the given folder ID. Multilevel folders are not
        supported. You can also see the Quick reference topic for
        additional information on this.
        Items in a folder are stored by reference and are not physically in
        a folder. Rather, they're stored as links to the original item, e.g.
        /content/items/<itemId>.

        Inputs:
           username - name of user to query
        """
        url = self._url + "/users/%s" % username
        params = {
            "f" : "json",
            "token" : self._securityHandler.token
        }
        return self._do_get(url=url,
                             param_dict=params,
                             proxy_url=self._proxy_url,
                             proxy_port=self._proxy_port)
    #----------------------------------------------------------------------
    def groupContent(self, groupId):
        """
        The group's content provides access to the items that are shared
        with the group.
        Group items are stored by reference and are not physically stored
        in a group. Rather, they are stored as links to the original item
        in the item resource (/content/items/<itemId>).
        Available only to the users of the group and the administrator of
        the organization to which the group belongs, if any.

        Inputs:
           groupId - unique group identifier
        """
        url = self._url + "/groups/%s" % groupId
        params = {
            "f" : "json",
            "token" : self._securityHandler.token
        }
        return self._do_get(url=url,
                             param_dict=params,
                             proxy_url=self._proxy_url,
                             proxy_port=self._proxy_port)
    #----------------------------------------------------------------------
    def item(self, itemId):
        """ returns the Item class for a given item id """
        return Item(itemId=itemId,
                    url=self._url,
                    securityHandler=self._securityHandler,
                    proxy_url=self._proxy_url,
                    proxy_port=self._proxy_port,
                    initialize=False)
    #----------------------------------------------------------------------
    def usercontent(self, username):
        """
        returns the user content class for a given user
        """
        return UserContent(username=username,
                           url=self._url,
                           securityHandler=self._securityHandler,
                           proxy_url=self._proxy_url,
                           proxy_port=self._proxy_port)



########################################################################
class FeatureContent(BaseAGOLClass):
    """
    Feature Content Root is the parent resource for feature operations such
    as Analyze and Generate.
    """
    _baseURL = None
    _url = None
    _securityHandler = None
    _proxy_port = None
    _proxy_url = None
    #----------------------------------------------------------------------
    def __init__(self, url, securityHandler,
                 proxy_url=None,
                 proxy_port=None):
        """Constructor"""
        if url.lower().find("/features") < 0:
            self._url = url + "/features"
        else:
            self._url = url
        self._securityHandler = securityHandler
        self._proxy_port = proxy_port
        self._proxy_url = proxy_url
    #----------------------------------------------------------------------
    @property
    def featureContentRoot(self):
        """ returns the feature content root url """
        return self._url
    #----------------------------------------------------------------------
    def analyze(self,
                itemId=None,
                filePath=None,
                text=None,
                fileType="csv",
                analyzeParameters={}):
        """
        The Analyze call helps a client analyze a CSV file prior to
        publishing or generating features using the Publish or Generate
        operation, respectively.
        Analyze returns information about the file including the fields
        present as well as sample records. Analyze attempts to detect the
        presence of location fields that may be present as either X,Y
        fields or address fields.
        Analyze packages its result so that publishParameters within the
        JSON response contains information that can be passed back to the
        server in a subsequent call to Publish or Generate. The
        publishParameters subobject contains properties that describe the
        resulting layer after publishing, including its fields, the desired
        renderer, and so on. Analyze will suggest defaults for the renderer.
        In a typical workflow, the client will present portions of the
        Analyze results to the user for editing before making the call to
        Publish or Generate.
        If the file to be analyzed currently exists in the portal as an
        item, callers can pass in its itemId. Callers can also directly
        post the file. In this case, the request must be a multipart post
        request pursuant to IETF RFC1867. The third option for text files
        is to pass the text in as the value of the text parameter.

        Inputs:
           itemid - The ID of the item to be analyzed.
           file - The file to be analyzed.
           text - The text in the file to be analyzed.
           filetype - The type of input file.
           analyzeParameters - A JSON object that provides geocoding information
        """
        files = []
        url = self._url + "/analyze"
        params = {
            "f" : "json",
            "token" : self._securityHandler.token

        }
        fileType = "csv"
        params["fileType"] = fileType
        if analyzeParameters is not None:
            params['analyzeParameters'] = analyzeParameters

        if os.path.isfile(filePath):
            params['text'] = open(filePath, 'rb').read()
            return self._do_post(url=url, param_dict=params,
                                 proxy_url=self._proxy_url,
                                 proxy_port=self._proxy_port)
        elif itemId is not None:
            params["fileType"] = fileType
            params['itemId'] = itemId
            return self._do_post(url=url, param_dict=params,
                                 proxy_url=self._proxy_url,
                                 proxy_port=self._proxy_port)
        else:
            raise AttributeError("either an Item ID or a file path must be given.")
    #----------------------------------------------------------------------
    def generate(self,
                 publishParameters,
                 itemId=None,
                 filePath=None,
                 fileType=None
                 ):
        """
        The Generate call helps a client generate features from a CSV file
        or a shapefile.
        CSV files that contain location fields (either address fields or X,
        Y fields) are spatially enabled by the Generate operation.
        The result of Generate is a JSON feature collection.
        If the file to be analyzed already exists in the portal as an item,
        callers can pass in its itemId. Callers can also directly post the
        file. In this case, the request must be a multipart post request
        pursuant to IETF RFC1867. The third option for text files is to
        pass the text in as the value of the text parameter.
        Generate requires that the caller pass in publish parameters that
        describe the layers in the feature collection to be generated.

        Inputs:
           publishParameters - A JSON object describing the layer and
                               service to be created as part of the Publish
                               operation. The appropriate value for publish
                               parameters depends on the file type being
                               published. (Python Dictionary)
           itemId - unique id of item to generate
           filePath - path to zipped shapefile or csv
           fileType - either shapefile or csv
        """
        allowedFileTypes = ['shapefile', 'csv']
        files = []
        url = self._url + "/generate"
        params = {
            "f" : "json",
            "token" : self._securityHandler.token
        }
        params['publishParameters'] = publishParameters
        parsed = urlparse.urlparse(url)
        if fileType.lower() not in allowedFileTypes and \
           filePath is not None:
            raise AttributeError("fileType must be either shapefile or csv when specifying a file")
        if filePath is not None:
            params['type'] = fileType

            if fileType.lower() == "csv":
                params['text'] = open(filePath,'rb').read()
                return self._do_post(url=url, param_dict=params,
                                     proxy_url=self._proxy_url,
                                     proxy_port=self._proxy_port)
            else:
                files.append(('file', filePath, os.path.basename(filePath)))
                res = self._post_multipart(host=parsed.hostname,
                                           port=parsed.port,
                                           selector=parsed.path,
                                           fields=params,
                                           files=files,
                                           ssl=parsed.scheme.lower() == 'https',
                                           proxy_url=self._proxy_url,
                                           proxy_port=self._proxy_port)
                return res
        elif itemId is not None:
            params["fileType"] = fileType
            params['itemId'] = itemId
            return self._do_post(url=url, param_dict=params,
                                 proxy_url=self._proxy_url,
                                 proxy_port=self._proxy_port)
########################################################################
class Item(BaseAGOLClass):
    """
    Modifies existing items based on an item Id.
    This class is ment for administrators/owners to modify existing
    contents on the AGOL/Portal site.
    """
    _baseURL = None
    _url = None
    _securityHandler = None
    _proxy_port = None
    _proxy_url = None
    _itemId = None
    #  From Service
    _appCategories = None
    _uploaded = None
    _properties = None
    _documentation = None
    _item = None
    _id = None
    _owner = None
    _created = None
    _modified = None
    _lastModified = None
    _name = None
    _title = None
    _url = None
    _itemType = None
    _guid = None
    _typeKeywords = None
    _description = None
    _tags = None
    _snippet = None
    _thumbnail = None
    _extent = None
    _spatialReference = None
    _accessInformation = None
    _licenseInfo = None
    _culture = None
    _access = None
    _industries = None
    _languages = None
    _largeThumbnail = None
    _banner = None
    _screenshots = None
    _listed = None
    _ownerFolder = None
    _size = None
    _protected = None
    _commentsEnabled = None
    _numComments = None
    _numRatings = None
    _avgRating = None
    _numViews = None
    _type = None
    #----------------------------------------------------------------------
    def __init__(self, itemId, url,
                 securityHandler,
                 proxy_url=None,
                 proxy_port=None,
                 initialize=False):
        """Constructor"""
        if url.lower().endswith("/items") == False:
            self._baseUrl = url + "/items"
        else:
            self._baseUrl = url
        self._itemId = itemId
        self._securityHandler = securityHandler
        self._proxy_port = proxy_port
        self._proxy_url = proxy_url
        if initialize:
            self.__init()
    #----------------------------------------------------------------------
    def __init(self):
        """ loads the data into the class """

        param_dict = {"f": "json",
                      "token" : self._securityHandler.token
        }
        json_dict = self._do_get(self._baseUrl + "/%s" % self._itemId, param_dict,
                                 proxy_url=self._proxy_url,
                                 proxy_port=self._proxy_port)
        attributes = [attr for attr in dir(self)
                    if not attr.startswith('__') and \
                    not attr.startswith('_')]
        for k,v in json_dict.iteritems():
            if k in attributes:
                setattr(self, "_"+ k, json_dict[k])
            elif k == 'error':
                print json_dict[k]
            else:
                print k, " - attribute not implmented in the class _content.Item."
    #----------------------------------------------------------------------
    @property
    def itemId(self):
        """ get/set id passed by the user """
        return self._itemId
    #----------------------------------------------------------------------
    @itemId.setter
    def itemId(self, value):
        """ get/set id passed by the user """
        if value != self._itemId and \
           value is not None:
            self._itemId = value
            self.__init()
    #----------------------------------------------------------------------
    @property
    def type(self):
        """ returns the item type """
        if self._type is None:
            self.__init()
        return self._type
    #----------------------------------------------------------------------
    @property
    def modified(self):
        """ returns last modified in UNIX time """
        if self._modified is None:
            self.__init()
        return self._modified
    #----------------------------------------------------------------------
    @property
    def guid(self):
        """ returns the guid of the item """
        if self._guid is None:
            self.__init()
        return self._guid

    #----------------------------------------------------------------------
    @property
    def uploaded(self):
        """ date the item is uploaded in UNIX time """
        if self._uploaded is None:
            self.__init()
        return self._uploaded
    #----------------------------------------------------------------------
    @property
    def properties(self):
        """ returns the items properties """
        if self._properties is None:
            self.__init()
        return self._properties
    #----------------------------------------------------------------------
    @property
    def documentation(self):
        """ returns the items documentation """
        if self._documentation is None:
            self.__init()
        return self._documentation
    #----------------------------------------------------------------------
    @property
    def item(self):
        """ returns the item """
        if self._item is None:
            self.__init()
        return self._item
    #----------------------------------------------------------------------
    @property
    def id(self):
        """ the unique ID for this item """
        if self._id is None:
            self.__init()
        return self._id
    #----------------------------------------------------------------------
    @property
    def owner(self):
        """the username of the owner """
        if self._owner is None:
            self.__init()
        return self._owner
    #----------------------------------------------------------------------
    @property
    def created(self):
        """ date the item was created in UNIX time (milliseconds) """
        if self._created is None:
            self.__init()
        return self._created
    #----------------------------------------------------------------------
    @property
    def lastModified(self):
        """ the date the item was last modified in UNIX time """
        if self._lastModified is None:
            self.__init()
        return self._lastModified
    #----------------------------------------------------------------------
    @property
    def appCategories(self):
        """ displays the application category"""
        if self._appCategories is None:
            self.__init()
        return self._appCategories

    #----------------------------------------------------------------------
    @property
    def name(self):
        """ file name of the item for file types """
        if self._name is None:
            self.__init()
        return self._name
    #----------------------------------------------------------------------
    @property
    def title(self):
        """ title of the item """
        if self._title is None:
            self.__init()
        return self._title
    #----------------------------------------------------------------------
    @property
    def url(self):
        """" the URL for the resource """
        if self._url is None:
            self.__init()
        return self._url
    #----------------------------------------------------------------------
    @property
    def itemType(self):
        """ GIS content type of the item """
        if self._type is None:
            self.__init()
        return self._type
    #----------------------------------------------------------------------
    @property
    def typeKeywords(self):
        """
        a set of keywords that further describes the type of this item
        """
        if self._typeKeywords is None:
            self.__init()
        return self._typeKeywords
    #----------------------------------------------------------------------
    @property
    def description(self):
        """
        item description
        """
        if self._description is None:
            self.__init()
        return self._description
    #----------------------------------------------------------------------
    @property
    def tags(self):
        """ user defined tags that describe the item """
        if self._tags is None:
            self.__init()
        return self._tags
    #----------------------------------------------------------------------
    @property
    def snippet(self):
        """ a short summary description of item """
        if self._snippet is None:
            self.__init()
        return self._snippet
    #----------------------------------------------------------------------
    @property
    def thumbnail(self):
        """ URL to the thumbnail used for the item """
        if self._thumbnail is None:
            self.__init()
        return self._thumbnail
    #----------------------------------------------------------------------
    @property
    def extent(self):
        """ bounding rectangle for the item in WGS84 """
        if self._extent is None:
            self.__init()
        return self._extent
    #----------------------------------------------------------------------
    @property
    def spatialReference(self):
        """The coordinate system of the item."""
        if self._spatialReference is None:
            self.__init()
        return self._spatialReference
    #----------------------------------------------------------------------
    @property
    def accessInformation(self):
        """Information on the source of the item."""
        if self._accessInformation is None:
            self.__init()
        return self._accessInformation
    #----------------------------------------------------------------------
    @property
    def licenseInfo(self):
        """license information or restrictions"""
        if self._licenseInfo is None:
            self.__init()
        return self._licenseInfo
    #----------------------------------------------------------------------
    @property
    def culture(self):
        """ item locale information """
        if self._culture is None:
            self.__init()
        return self._culture
    #----------------------------------------------------------------------
    @property
    def access(self):
        """ indicates the level of access to the item """
        if self._access is None:
            self.__init()
        return self._access
    #----------------------------------------------------------------------
    @property
    def industries(self):
        """primarily applies to industries associated with the app """
        if self._industries is None:
            self.__init()
        return self._industries
    #----------------------------------------------------------------------
    @property
    def languages(self):
        """ languages assocaited with application """
        if self._languages is None:
            self.__init()
        return self._languages
    #----------------------------------------------------------------------
    @property
    def largeThumbnail(self):
        """ URL to thumbnail for application """
        if self._largeThumbnail is None:
            self.__init()
        return self._largeThumbnail
    #----------------------------------------------------------------------
    @property
    def banner(self):
        """ URL to the banner used for the application """
        if self._banner is None:
            self.__init()
        return self._banner
    #----------------------------------------------------------------------
    @property
    def screenshots(self):
        """ URL to the screenshots used by the application """
        if self._screenshots is None:
            self.__init()
        return self._screenshots
    #----------------------------------------------------------------------
    @property
    def listed(self):
        """ if true, item is in the marketplace """
        if self._listed is None:
            self.__init()
        return self._listed
    #----------------------------------------------------------------------
    @property
    def ownerFolder(self):
        """ ID of the folder in which the owner stored the item """
        if self._ownerFolder is None:
            self.__init()
        return self._ownerFolder
    #----------------------------------------------------------------------
    @property
    def size(self):
        """ size of the item """
        if self._size is None:
            self.__init()
        return self._size
    #----------------------------------------------------------------------
    @property
    def protected(self):
        """ proctects the item from deletion """
        if self._protected is None:
            self.__init()
        return self._protected
    #----------------------------------------------------------------------
    @property
    def commentsEnabled(self):
        """ indicates if comments are allowed on the item """
        if self._commentsEnabled is None:
            self.__init()
        return self._commentsEnabled
    #----------------------------------------------------------------------
    @property
    def numComments(self):
        """Number of comments on the item."""
        if self._numComments is None:
            self.__init()
        return self._numComments
    #----------------------------------------------------------------------
    @property
    def numRatings(self):
        """ number of ratings on the item """
        if self._numRatings is None:
            self.__init()
        return self._numRatings
    #----------------------------------------------------------------------
    @property
    def avgRating(self):
        """ average rating """
        if self._avgRating is None:
            self.__init()
        return self._avgRating
    #----------------------------------------------------------------------
    @property
    def numViews(self):
        """ numbers of views of the item """
        if self._numViews is None:
            self.__init()
        return self._numViews
    #----------------------------------------------------------------------
    def addComment(self, comment):
        """ adds a comment to a given item.  Must be authenticated """
        url = self._baseUrl + "/%s/addComment" % self._itemId
        params = {
            "f" : "json",
            "comment" : comment,
            "token" : self._securityHandler.token
        }
        return self._do_post(url, params, proxy_port=self._proxy_port,
                             proxy_url=self._proxy_url)
    #----------------------------------------------------------------------
    def addRating(self, rating=5.0):
        """Adds a rating to an item between 1.0 and 5.0"""
        if rating > 5.0:
            rating = 5.0
        elif rating < 1.0:
            rating = 1.0
        url = self._baseUrl + "/%s/addRating" % self._itemId
        params = {
            "f": "json",
            "token" : self._securityHandler.token,
            "rating" : "%s" % rating
        }
        return self._do_post(url,
                             params,
                             proxy_port=self._proxy_port,
                             proxy_url=self._proxy_url)
    #----------------------------------------------------------------------
    def deleteComment(self, commentId):
        """ removes a comment from an Item

        Inputs:
           commentId - unique id of comment to remove
        """
        url = self._baseUrl + "/%s/comments/%s/delete" % (self._itemId, commentId)
        params = {
            "f": "json",
            "token" : self._securityHandler.token
        }
        return self._do_post(url,
                             params,
                             proxy_port=self._proxy_port,
                             proxy_url=self._proxy_url)
    #----------------------------------------------------------------------
    def deleteRating(self):
        """"""
        url = self._baseUrl + "/%s/deleteRating" % self._itemId
        params = {
            "f": "json",
            "token" : self._securityHandler.token
        }
        return self._do_post(url,
                             params,
                             proxy_port=self._proxy_port,
                             proxy_url=self._proxy_url)
    #----------------------------------------------------------------------
    @property
    def groups(self):
        """ returns a list of groups the item is shared with. """
        url = self._baseUrl + "/%s/groups" % self._itemId
        params = {
            "f": "json",
            "token" : self._securityHandler.token
        }
        return self._do_get(url,
                             params,
                             proxy_port=self._proxy_port,
                             proxy_url=self._proxy_url)
    #----------------------------------------------------------------------
    def itemComment(self, commentId):
        """ returns details of a single comment """
        url = self._baseUrl + "/%s/comments/%s" % (self._itemId, commentId)
        params = {
            "f": "json",
            "token" : self._securityHandler.token
        }
        return self._do_get(url,
                            params,
                            proxy_port=self._proxy_port,
                             proxy_url=self._proxy_url)
    #----------------------------------------------------------------------
    @property
    def itemComments(self):
        """ returns all comments for a given item """
        url = self._baseUrl + "/%s/comments/" % self._itemId
        params = {
            "f": "json",
            "token" : self._securityHandler.token
        }
        return self._do_get(url,
                            params,
                            proxy_port=self._proxy_port,
                            proxy_url=self._proxy_url)
    #----------------------------------------------------------------------
    def itemData(self, f="json", filePath=None):
        """ returns data for an item on agol/portal

        Inputs:
           f - output format either zip of json
        """

        params = {
            "f" : f,
            "token" : self._securityHandler.token
        }
        url = self._baseUrl + "/%s/data" % self._itemId
        if self.type.lower() in ["shapefile"]:
            save_path = os.path.dirname(filePath)
            file_name = os.path.basename(filePath)
            url =  url + "?%s" % urllib.urlencode(params)
            return self._download_file(url,
                                       save_path=save_path,
                                       file_name=file_name,
                                       proxy_port=self._proxy_port,
                                       proxy_url=self._proxy_url)
        else:
            return self._do_get(url, params, proxy_port=self._proxy_port,
                                proxy_url=self._proxy_url)
    #----------------------------------------------------------------------
    def itemInfoFile(self):
        """  """
        url = self._baseUrl + "/%s/info/iteminfo.xml" % self._itemId
        xml = self._download_file(
            url=url,
            save_path=os.environ['TEMP'],
            file_name="iteminfo.xml",
            proxy_url=self._proxy_url,
            proxy_port=self._proxy_port
        )
        text = open(xml, 'rb').read()
        os.remove(xml)
        return text
    #----------------------------------------------------------------------
    @property
    def itemRating(self):
        """ returns the item's rating """
        url = self._baseUrl + "/%s/rating" % self._itemId
        params = {
            "f": "json",
            "token" : self._securityHandler.token
        }
        return self._do_get(url,
                            params,
                            proxy_port=self._proxy_port,
                            proxy_url=self._proxy_url)
    #----------------------------------------------------------------------
    def packageInfoFile(self, saveFolder):
        """
        The Package Info File for the uploaded item is only available for
        items that are ArcGIS packages (for example, Layer Package, Map
        Package). It contains information that is used by clients (ArcGIS
        Desktop, ArcGIS Explorer, and so on) to work appropriately with
        downloaded packages.
        Inputs:
           saveFolder - location to save the package file
        """
        saveFile = saveFolder + os.sep + "item.pkinfo"
        if os.path.isfile(saveFile):
            os.remove(saveFile)
        url = self._baseUrl + "/%s/item.pkinfo" % self._itemId
        xml = self._download_file(
            url=url,
            save_path=saveFolder,
            file_name=os.path.basename(saveFile),
            proxy_url=self._proxy_url,
            proxy_port=self._proxy_port
        )
        return xml
    #----------------------------------------------------------------------
    def relatedItems(self, relationshipType, direction=None):
        """
        Gets all the related items of a certain relationship type for that
        item. An optional direction can be specified if the direction of
        the relationship is ambiguous. Otherwise, the service will try to
        infer it.

        Inputs:
           relationshipType - The type of relationship between the two items
           direction - The direction of the relationship. Either forward
                       (from origin -> destination) or reverse (from
                       destination -> origin).
        """
        url = self._baseUrl + "/%s/relatedItems" % self._itemId
        params = {
            "f": "json",
            "token" : self._securityHandler.token,
            "relationshipType" : relationshipType
        }
        if direction is not None:
            params['direction'] = direction
        return self._do_get(url,
                            params,
                            proxy_port=self._proxy_port,
                            proxy_url=self._proxy_url)
    #----------------------------------------------------------------------
    def shareItem(self,
                  groups="",
                  everyone=False,
                  org=False):
        """
        Shares a batch of items with the specified list of groups. Users
        can only share items with groups to which they belong.
        This operation also allows a user to share items with everyone, in
        which case the items are publicly accessible, or with everyone in
        their organization.

        Inputs:
           groups - comma seperate list of group Ids
           everyone - boolean, true means share with all
           org - boolean trues means share with orginization
        """
        params = {
            "f": "json",
            "token" : self._securityHandler.token,
            "everyone" : everyone,
            "org" : org
        }
        if groups != "" and groups is not None:
            params['groups'] = groups
        url = self._baseUrl + "/%s/share" % self._itemId
        return self._do_post(
            url = url,
            param_dict=params,
            proxy_url=self._proxy_url,
            proxy_port=self._proxy_port)
    #----------------------------------------------------------------------
    def unshareItem(self, groups):
        """
        Stops sharing the item with the specified list of groups

        Inputs:
           groups - comma seperated list of Ids
        """
        params = {
            "f": "json",
            "token" : self._securityHandler.token,
            "groups" : groups
        }
        url = self._baseUrl + "/%s/unshare" % self._itemId
        return self._do_post(
            url = url,
            param_dict=params,
            proxy_url=self._proxy_url,
            proxy_port=self._proxy_port)

########################################################################
class UserItems(BaseAGOLClass):
    """
    Helps manage a given owner's content
    """
    _username =  None
    _itemId = None
    _baseUrl = None
    _securityHandler = None
    _proxy_url = None
    _proxy_port = None

    #----------------------------------------------------------------------
    def __init__(self,
                 username,
                 itemId,
                 url,
                 securityHanlder,
                 proxy_url=None,
                 proxy_port=None):
        """Constructor"""

        self._username = username
        self._itemId = itemId
        if url.lower().endswith("/users") == False:
            self._baseUrl = url + "/users" % username
        else:
            self._baseUrl = url
        self._securityHandler = securityHanlder
        self._proxy_url = proxy_url
        self._proxy_port = proxy_port
    #----------------------------------------------------------------------
    @property
    def itemId(self):
        """gets/sets the item id"""
        return self._itemId
    #----------------------------------------------------------------------
    @itemId.setter
    def itemId(self, value):
        """gets/sets the item id"""
        if self._itemId != value:
            self._itemId = value
    #----------------------------------------------------------------------
    @property
    def username(self):
        """gets/sets the username"""
        return self._username
    #----------------------------------------------------------------------
    @username.setter
    def username(self, value):
        """gets/sets the username"""
        if self._username != value:
            self._username = value
    #----------------------------------------------------------------------
    def deleteItem(self):
        """
        The Delete Item operation (POST only) removes both the item and its
        link from the user's folder by default. This operation is available
        to the user and to the administrator of the organization to which
        the user belongs.

        """
        params = {
            "f" : "json",
            "token" : self._securityHandler.token
        }
        url = self._baseUrl + "/%s/items/%s/delete" % (self._username, self._itemId)
        return self._do_post(
            url = url,
            param_dict=params,
            proxy_url=self._proxy_url,
            proxy_port=self._proxy_port)
    #----------------------------------------------------------------------
    def moveItem(self, folder="/"):
        """
        The Move Item operation moves the item (link) from the current
        folder to the specified target folder. Moving an item link does not
        change the URI of the item itself, which continues to be
        /content/items/<itemId>.

        Inputs:
           folder - the destination folder ID for the item. If the item is
                    to be moved to the root folder, specify the value as /
                    (forward slash).

                    Example 1: folder=/ (move to root folder)
                    Example 2: folder=1a9ad803da604628b08c968ce602a231
                    (move to folder with ID 1a9ad803da604628b08c968ce602a231)
        """
        params = {
            "f" : "json",
            "token" : self._securityHandler.token,
            "folder" : folder
        }
        url = self._baseUrl + "/%s/items/%s/move" % (self._username, self._itemId)
        return self._do_post(
            url = url,
            param_dict=params,
            proxy_url=self._proxy_url,
            proxy_port=self._proxy_port)
    #----------------------------------------------------------------------
    def protect(self):
        """
        The Protect operation protects the items from deletion. This
        operation is available to the user and to the administrator of the
        organization to which the user belongs
        """
        params = {
            "f" : "json",
            "token" : self._securityHandler.token
        }
        url = self._baseUrl + "/%s/items/%s/protect" % (self._username, self._itemId)
        return self._do_post(
            url = url,
            param_dict=params,
            proxy_url=self._proxy_url,
            proxy_port=self._proxy_port)
    #----------------------------------------------------------------------
    def reassignItem(self,
                     targetUsername,
                     targetFoldername):
        """
        The Reassign Item operation allows the administrator of an
        organization to reassign a member's item to another member of the
        organization.

        Inputs:
           targetUsername - The target username of the new owner of the
                            item
           targetFoldername - The destination folder for the item. If the
                              item is to be moved to the root folder,
                              specify the value as "/" (forward slash). If
                              the target folder doesn't exist, it will be
                              created automatically.
        """
        params = {
            "f" : "json",
            "token" : self._securityHandler.token,
            "targetUsername" : targetUsername,
            "targetFoldername" : targetFoldername
        }
        url = self._baseUrl + "/%s/items/%s/reassign" % (self._username, self._itemId)
        return self._do_post(
            url = url,
            param_dict=params,
            proxy_url=self._proxy_url,
            proxy_port=self._proxy_port)
    #----------------------------------------------------------------------
    def shareItem(self,
                  everyone=False,
                  org=False,
                  groups=""):
        """
        Shares a batch of items with the specified list of groups. Users
        can only share items with groups to which they belong.
        This operation also allows a user to share items with everyone, in
        which case the items are publicly accessible, or with everyone in
        their organization.

        Inputs:
           groups - comma seperate list of group Ids
           everyone - boolean, true means share with all
           org - boolean trues means share with orginization
        """
        params = {
            "f": "json",
            "token" : self._securityHandler.token,
            "everyone" : everyone,
            "org" : org
        }
        if groups != "" and groups is not None:
            params['groups'] = groups
        url = self._baseUrl + "/%s/items/%s/share" % (self._username, self._itemId)
        return self._do_post(
            url = url,
            param_dict=params,
            proxy_url=self._proxy_url,
            proxy_port=self._proxy_port)
    #----------------------------------------------------------------------
    def unprotect(self):
        """
        The Unprotect operation disables the item protection from deletion.
        """
        params = {
            "f": "json",
            "token" : self._securityHandler.token,

        }
        url = self._baseUrl + "/%s/items/%s/unprotect" % (self._username, self._itemId)
        return self._do_post(
            url = url,
            param_dict=params,
            proxy_url=self._proxy_url,
            proxy_port=self._proxy_port)
    #----------------------------------------------------------------------
    def unshareItem(self, groups):
        """
        Stops sharing the item with the specified list of groups. Available
        to the user and the administrator of the organization to which the
        user belongs, if any.

        Inputs:
           groups - comma seperated list of group Ids
        """
        params = {
            "f": "json",
            "token" : self._securityHandler.token,
            "groups": groups

        }
        url = self._baseUrl + "/%s/items/%s/unshare" % (self._username, self._itemId)
        return self._do_post(
            url = url,
            param_dict=params,
            proxy_url=self._proxy_url,
            proxy_port=self._proxy_port)
    #----------------------------------------------------------------------
    def updateItem(self,
                   itemParameter,
                   clearEmptyFields=False,
                   data=None,
                   metadata=None,
                   ):
        """
        updates an item's properties using the ItemParameter class.

        Inputs:
           itemParameter - property class to update
           clearEmptyFields - boolean, cleans up empty values
           data - updates the file property of the service like a .sd file
        """
        thumbnail = None
        files = []
        params = {
            "f": "json",
            "token" : self._securityHandler.token,
            "clearEmptyFields": clearEmptyFields
        }

        if isinstance(itemParameter, ItemParameter) == False:
            raise AttributeError("itemParameter must be of type parameter.ItemParameter")
        keys_to_delete = ['id', 'owner', 'size', 'numComments',
                          'numRatings', 'avgRating', 'numViews' ]
        dictItem = itemParameter.value
        for key in keys_to_delete:
            if key in dictItem:
                del dictItem[key]

        for k,v in dictItem:
            if key == "thumbnail":
                thumbnail = dictItem['thumbnail']
                files.append(('thumbnail', thumbnail, os.path.basename(thumbnail)))
                del dictItem['thumbnail']
            elif key == "metadata":
                files.append(('metadata', metadata, 'metadata.xml'))
            else:
                params[key] = dictItem[key]
        if data is not None:
            files.append(('file', data, os.path.basename(data)))

        url = self._baseUrl + "/%s/items/%s/update" % (self._username, self._itemId)
        parsed = urlparse.urlparse(url)

        res = self._post_multipart(host=parsed.hostname,
                                   port=parsed.port,
                                   selector=parsed.path,
                                   fields=params,
                                   files=files,
                                   ssl=parsed.scheme.lower() == 'https',
                                   proxy_url=self._proxy_url,
                                   proxy_port=self._proxy_port)
        return res

########################################################################
class UserContent(BaseAGOLClass):
    """
    manages a given user's content
    """
    _username = None
    _baseUrl = None
    _securityHandler = None
    _proxy_url = None
    _proxy_port = None
    #----------------------------------------------------------------------
    def __init__(self,
                 username,
                 url,
                 securityHandler,
                 proxy_url=None,
                 proxy_port=None):
        """Constructor"""
        self._username = username
        self._securityHandler = securityHandler
        self._proxy_url = proxy_url
        self._proxy_port = proxy_port

        if url.lower().endswith("/users") == False:
            url += "/users"
            self._baseUrl = url
        else:
            self._baseUrl = url
    #----------------------------------------------------------------------
    @property
    def username(self):
        """gets/sets the username"""
        return self._username
    #----------------------------------------------------------------------
    @username.setter
    def username(self, value):
        """gets/sets the username"""
        if self._username != value:
            self._username = value
    #----------------------------------------------------------------------
    def addItem(self,
                itemParameters,
                filePath=None,
                overwrite=False,
                folder=None,
                url=None,
                text=None,
                relationshipType=None,
                originItemId=None,
                destinationItemId=None,
                serviceProxyParams=None,
                metadata=None):
        """
        """
        params = {
            "f" : "json",
            "token" : self._securityHandler.token,
            "overwrite" : overwrite
        }
        #"overwrite" : overwrite
        if itemParameters is not None:
            params.update(itemParameters.value)
        if url is not None:
            params['url'] = url
        if text is not None:
            params['text'] = text
        if relationshipType is not None:
            params['relationshipType'] = relationshipType
        if originItemId is not None:
            params['originItemId'] = originItemId
        if destinationItemId is not None:
            params['destinationItemId'] = destinationItemId
        if serviceProxyParams is not None:
            params['serviceProxyParams'] = serviceProxyParams

        url = self._baseUrl + "/%s" % self._username
        url = url.replace("http://", "https://" )
        if folder is not None:
            url += '/' + folder
        url += '/addItem'
        parsed = urlparse.urlparse(url)
        files = []
        if filePath is not None and os.path.isfile(filePath):
            files.append(('file', filePath, os.path.basename(filePath)))
            params["filename"] = os.path.basename(filePath)
        if 'thumbnail' in params:
            v = params['thumbnail']
            del params['thumbnail']
            files.append(('thumbnail', v, os.path.basename(v)))
        if metadata is not None and os.path.isfile(metadata):
            files.append(('metadata', metadata, 'metadata.xml'))
        if len(files) < 1:
            res = self._do_post(url,
                                param_dict=params,
                                proxy_url=self._proxy_url,
                                proxy_port=self._proxy_port)
        else:
            params['itemType'] = 'file'
            params['async'] = False
            res = self._post_multipart(host=parsed.hostname,
                                       selector=parsed.path,
                                       files = files,
                                       fields=params,
                                       port=parsed.port,
                                       ssl=parsed.scheme.lower() == 'https',
                                       proxy_port=self._proxy_port,
                                       proxy_url=self._proxy_url)
        res = self._unicode_convert(res)
        return res
    #----------------------------------------------------------------------
    def addRelationship(self,
                        originItemId,
                        destinationItemId,
                        relationshipType):
        """
        Adds a relationship of a certain type between two items.

        Inputs:
           originItemId - The item ID of the origin item of the
                          relationship
           destinationItemId - The item ID of the destination item of the
                               relationship.
           relationshipType - The type of relationship between the two
                              items. Must be defined in Relationship types.
        """
        url = self._baseUrl + "/%s/addRelationship" % self._username
        params = {
            "originItemId" : originItemId,
            "destinationItemId": destinationItemId,
            "relationshipType" : relationshipType,
            "f" : "json",
            "token" : self._securityHandler.token
        }
        return self._do_post(url=url,
                             param_dict=params,
                             proxy_port=self._proxy_port,
                             proxy_url=self._proxy_url)
    #----------------------------------------------------------------------
    def cancel(self, itemId):
        """
        Cancels a multipart upload on an item. Can be called after the
        multipart Add Item or Update Item call is made but cannot be called
        after a Commit operation.

        Inputs:
           itemId - unique item id
        """
        url = self._baseUrl + "/%s/%s/cancel" % (self._username, itemId)
        params = {
            "f" : "json",
            "token" : self._securityHandler.token
        }
        return self._do_post(url=url,
                             param_dict=params,
                             proxy_port=self._proxy_port,
                             proxy_url=self._proxy_url)
    #----------------------------------------------------------------------
    def commit(self, itemId):
        """
        Commit is called once all parts are uploaded during a multipart Add
        Item or Update Item operation. The parts are combined into a file,
        and the original file is overwritten during an Update Item
        operation. This is an asynchronous call and returns immediately.
        Status can be used to check the status of the operation until it is
        completed.

        Inputs:
           itemId - unique item id
        """
        url = self._baseUrl + "/%s/%s/commit" % (self._username, itemId)
        params = {
            "f" : "json",
            "token" : self._securityHandler.token
        }
        return self._do_post(url=url,
                             param_dict=params,
                             proxy_port=self._proxy_port,
                             proxy_url=self._proxy_url)
    #----------------------------------------------------------------------
    def createFolder(self, name):
        """
        Creates a folder in which items can be placed. Folders are only
        visible to a user and solely used for organizing content within
        that user's content space.
        """
        url = self._baseUrl + "/%s/createFolder" % self._username
        params = {
            "f" : "json",
            "token" : self._securityHandler.token,
            "title" : name
        }
        return self._do_post(url=url,
                             param_dict=params,
                             proxy_port=self._proxy_port,
                             proxy_url=self._proxy_url)
    #----------------------------------------------------------------------
    def createService(self, createServiceParameter):
        """
        The Create Service operation allows users to create a hosted
        feature service. You can use the API to create an empty hosted
        feaure service from feature service metadata JSON.

        Inputs:
           createServiceParameter - create service object
        """
        url = self._baseUrl + "/%s/createService" % self._username
        val = createServiceParameter.value
        params = {
            "f" : "json",
            "token" : self._securityHandler.token,
            "outputType" : "featureService",
            "createParameters" : val
        }

        return self._do_post(url=url,
                             param_dict=params,
                             proxy_port=self._proxy_port,
                             proxy_url=self._proxy_url)
    #----------------------------------------------------------------------
    def deleteFolder(self, folderId):
        """
        The delete user folder operation (POST only) is available only on
        the user's non-root folders. The user's root folder cannot be
        deleted.
        Deleting a folder also deletes all items that it contains (both the
        items and the links are removed).

        Inputs:
           folderId - id of folder to remove
        """
        url = self._baseUrl + "/%s/%s/delete" % (self._username,
                                                 folderId)
        params = {
            "f" : "json",
            "token" : self._securityHandler.token
        }
        return self._do_post(url=url,
                             param_dict=params,
                             proxy_port=self._proxy_port,
                             proxy_url=self._proxy_url)
    #----------------------------------------------------------------------
    def deleteItems(self, items):
        """
        Deletes a batch of items owned or administered by the calling user.

        Inputs:
           items - A comma separated list of items to be deleted.
        """
        url = self._baseUrl + "/%s/deleteItems" % self._username
        params = {
            "f" : "json",
            "token" : self._securityHandler.token,
            "items" : items

        }
        return self._do_post(url=url,
                             param_dict=params,
                             proxy_port=self._proxy_port,
                             proxy_url=self._proxy_url)
    #----------------------------------------------------------------------
    def deleteRelationship(self,
                           originItemId,
                           destinationItemId,
                           relationshipType
                           ):
        """
        Deletes a relationship of a certain type between two items. The
        current user must have created the relationship to delete it. If
        the relationship does not exist, an error is thrown.

        Inputs:
           originItemId - The item ID of the origin item of the
                          relationship.
           destinationItemId -  item ID of the destination item of the
                               relationship.
           relationshipType -  type of relationship between the two items.
        """
        url = self._baseUrl + "/%s/deleteRelationship" % self._username
        params = {
            "f" : "json",
            "token" : self._securityHandler.token,
            "originItemId" : originItemId,
            "destinationItemid" : destinationItemId,
            "relationshipType" : relationshipType

        }
        return self._do_post(url=url,
                             param_dict=params,
                             proxy_port=self._proxy_port,
                             proxy_url=self._proxy_url)
    #----------------------------------------------------------------------
    def exportItem(self, title,
                   itemId,
                   exportFormat,
                   exportParameters=None):
        """
        Exports a service item (POST only) to the specified output format.
        Available only to users with an organizational subscription.
        Invokable only by the service item owner or an administrator.

        Inputs:
           title - name of export item
           itemId - id of the item to export
           exportFormat - out format. Values: Shapefile, CSV or File
                          Geodatabase
           exportParameters - A JSON object describing the layers to be
                              exported and the export parameters for each
                              layer.
        """
        url = self._baseUrl + '/%s/export' % self._securityHandler._username
        params = {
            "f" : "json",
            "token" : self._securityHandler.token,
            "title" : title,
            "itemId" : itemId,
            "exportFormat" : exportFormat,

        }
        if exportParameters is not None:
            params["exportParameters"] = json.dumps(exportParameters)
        return self._do_post(url=url,
                             param_dict=params,
                             proxy_port=self._proxy_port,
                             proxy_url=self._proxy_url)
    #----------------------------------------------------------------------
    def moveItems(self, items, folder="/"):
        """
        Moves a batch of items from their current folder to the specified
        target folder.

        Inputs:
           items - comma-seperated list of items to move
           folder - destination folder id. "/" means root
        """
        url = self._baseUrl + "/%s/moveItems" % self._username
        params = {
            "f" : "json",
            "token" : self._securityHandler.token,
            "items" : items,
            "folder" : folder

        }
        return self._do_post(url=url,
                             param_dict=params,
                             proxy_port=self._proxy_port,
                             proxy_url=self._proxy_url)
    #----------------------------------------------------------------------
    def publishItem(self,
                    fileType,
                    publishParameters=None,
                    itemId=None,
                    filePath=None,
                    text=None,
                    outputType=None
                    ):
        """
        Publishes a hosted service based on an existing source item.
        Publishers can create feature services as well as tiled map
        services.
        Feature services can be created using input files of type csv,
        shapefile, serviceDefinition, featureCollection, and
        fileGeodatabase.

        Inputs:
           fileType - Item type.
                      Values: serviceDefinition | shapefile | csv |
                      tilePackage | featureService | featureCollection |
                      fileGeodata
           publishParameters - object describing the service to be created
                               as part of the publish operation. Only
                               required for CSV, Shapefiles, feature
                               collection, and file geodatabase.
           itemId - The ID of the item to be published.
           text - The text in the file to be published. This ONLY applies
                  to CSV files.
           filePath - The file to be uploaded.
           outputType - Only used when a feature service is published as a
                        tile service.
        """
        _allowed_types = ["serviceDefinition", "shapefile", "csv",
                          "tilePackage", "featureService",
                          "featureCollection", "fileGeodata"]
        if fileType.lower() not in [t.lower() for t in _allowed_types]:
            raise AttributeError("Invalid fileType: %s" % fileType)
        url = self._baseUrl + "/%s/publish" % self._username
        params = {
            "f" : "json",
            "token" : self._securityHandler.token,
            'fileType': fileType

        }
        if publishParameters is not None and \
           isinstance(publishParameters, BaseParameters):
            params['publishParameters'] = publishParameters.value
        else:
            raise AttributeError("publishParameters in an invalid type")
        if itemId is not None:
            params['itemId'] = itemId
        if text is not None and fileType.lower() == 'csv':
            params['text'] = text
        if filePath is not None:
            parsed = urlparse.urlparse(url)
            files = []
            files.append(('file', filePath, os.path.basename(filePath)))
            res = self._post_multipart(host=parsed.hostname,
                                        selector=parsed.path,
                                        files = files,
                                        fields=params,
                                        port=parsed.port,
                                        ssl=parsed.scheme.lower() == 'https',
                                        proxy_port=self._proxy_port,
                                        proxy_url=self._proxy_url)
            res = self._unicode_convert(res)
            return res
        else:
            return self._do_post(url=url,
                                 param_dict=params,
                                 proxy_port=self._proxy_port,
                                 proxy_url=self._proxy_url)
    #----------------------------------------------------------------------
    def status(self, itemId, jobId, jobType=None):
        """
           Inquire about status when publishing an item, adding an item in
           async mode, or adding with a multipart upload. "Partial" is
           available for Add Item Multipart, when only a part is uploaded
           and the item is not committed.

           Input:
              jobType The type of asynchronous job for which the status has
                      to be checked. Default is none, which check the
                      item's status.  This parameter is optional unless
                      used with the operations listed below.
                      Values: publish, generateFeatures, export,
                              and createService
              jobId - The job ID returned during publish, generateFeatures,
                      export, and createService calls.
        """
        params = {
            "f" : "json",
            "token" : self._securityHandler.token,
            "jobId" : jobId,
            "jobType" : jobType
        }
        url = self._baseUrl + "/%s/items/%s/status" % (self._username, itemId)
        #https://www.arcgis.com/sharing/rest/content/users/andrewchap/items/378aedf2c04740088722e538261e7c73/status
        return self._do_get(url=url,
                            param_dict=params,
                            proxy_port=self._proxy_port,
                            proxy_url=self._proxy_url)

    #----------------------------------------------------------------------
    def shareItems(self, items, groups="", everyone=False,
                   org=False):
        """
        Shares a batch of items with the specified list of groups. Users
        can only share items with groups to which they belong. This
        operation also allows a user to share items with everyone, in which
        case the items are publicly accessible, or with everyone in their
        organization.

        Inputs:
           everyone - boolean, makes item public
           org - boolean, shares with all of the organization
           items - comma seperated list of items to share
           groups - comma sperated list of groups to share with
        """
        url = self._baseUrl + "/%s/shareItems" % self._username
        params = {
            "f" : "json",
            "token" : self._securityHandler.token,
            "items" : items,
            "everyone" : everyone,
            "org" : org,
            "groups" : groups


        }
        return self._do_post(url=url,
                             param_dict=params,
                             proxy_port=self._proxy_port,
                             proxy_url=self._proxy_url)
    #----------------------------------------------------------------------
    def unshareItems(self, items, groups):
        """
        Unshares a batch of items with the specified list of groups

        Inputs:
           items - comma-seperated list of items to unshare
           groups - comma-seperated list of groups to not share items with
        """
        url = self._baseUrl + "/%s/unshareItems" % self._username
        params = {
            "f" : "json",
            "token" : self._securityHandler.token,
            "items" : items,
            "groups" : groups
        }
        return self._do_post(url=url,
                             param_dict=params,
                             proxy_port=self._proxy_port,
                             proxy_url=self._proxy_url)
    #----------------------------------------------------------------------
    def updateItem(self,
                   itemId,
                   updateItemParameters,
                   clearEmptyFields=True,
                   filePath=None,
                   url=None,
                   text=None
                   ):
        """
        The Update Item operation allows users to update item information
        and their file, URL, or text depending on type. Users can use this
        operation to update item information such as title, description,
        tags, and so on, or use it to update an item's file, URL, or text.
        This call is available to the user and the administrator of the
        organization.

        Inputs:
           itemId - id of item to update
           updateItemParameters - ItemsParameter Object
           clearEmptyFields - boolean, Clears any fields that are passed in
                              empty
           filePath - path of the file that will update the online item
           url - The URL of the item to be updated.
           text - The text content for the item to be updated.
        """
        url = self._baseUrl + "/%s/items/%s/update" % (self._username, itemId)
        files = []
        parsed = urlparse.urlparse(url)
        params = {
            "f" : "json",
            "token" : self._securityHandler.token,
            "clearEmptyFields" : clearEmptyFields
        }
        if updateItemParameters is not None:
            params.update(updateItemParameters.value)
        if url is not None:
            params['url'] = url
        if text is not None:
            params['text'] = text
        if filePath is not None and \
           os.path.isfile(filePath):
            files.append(('file', filePath, os.path.basename(filePath)))
        if 'thumbnail' in params:
            v = params['thumbnail']
            del params['thumbnail']
            files.append(('thumbnail', v, os.path.basename(v)))
        res = self._post_multipart(host=parsed.hostname,
                                           selector=parsed.path,
                                           files = files,
                                           fields=params,
                                           port=parsed.port,
                                           ssl=parsed.scheme.lower() == 'https',
                                           proxy_port=self._proxy_port,
                                           proxy_url=self._proxy_url)
        res = self._unicode_convert(res)
        return res

















