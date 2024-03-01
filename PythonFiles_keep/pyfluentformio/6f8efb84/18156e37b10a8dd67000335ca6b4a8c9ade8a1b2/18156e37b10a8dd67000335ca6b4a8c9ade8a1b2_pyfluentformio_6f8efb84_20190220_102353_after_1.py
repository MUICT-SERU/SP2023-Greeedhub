import requests
import json
import pandas as pd


class Fluent:

    filterString = None
    selectString = None
    limitString = None
    populateString = None
    chunkSizeString = None
    firstChunk = None

    def __init__(self, baseUrl=None, resourcePath=None, token=None):
        self.baseUrl = baseUrl
        self.resourcePath = resourcePath
        self.token = token

    def filterToString(self, filters):
        filterString = ''

        for filter in filters:
            element = filter[0]
            query = filter[1]
            value = filter[2]

            if(query == '='):
                filterString = filterString + element + '=' + value + '&'
            elif(query == '!='):
                filterString = filterString + element + '__ne=' + value + '&'
            elif(query == '>'):
                filterString = filterString + element + '__gt=' + value + '&'
            elif(query == '>='):
                filterString = filterString + element + '__gte=' + value + '&'
            elif(query == '<'):
                filterString = filterString + element + '__lt=' + value + '&'
            elif(query == '<='):
                filterString = filterString + element + '__lte=' + value + '&'
            elif(query == 'in'):
                filterString = filterString + element + '__in=' + value + '&'
            elif(query == 'nin'):
                filterString = filterString + element + '__nin=' + value + '&'
            elif(query == 'exists'):
                filterString = filterString + element + '__exists=' + True + '&'
            elif(query == '!exists'):
                filterString = filterString + element + '__exists=' + False + '&'
            elif(query == 'regex'):
                filterString = filterString + element + '__regex=' + value + '&'

        return filterString[:-1]

    def selectToString(self, select):
        selectString = '_id,'

        for attribute in select:
            selectString = selectString + attribute + ','

        return selectString[:-1]

    def populateToString(self, resources):
        populateString = ''

        for resource in resources:
            populateString = populateString + resource + ','

        return populateString[:-1]

    def getQueryString(self):
        url = self.baseUrl + self.resourcePath + '/submission?'

        # Sets the final queryString
        # Adds the filterString
        if(isinstance(self.filterString, str)):
            url = url + self.filterString + '&'
        # Adds the selectString
        if(isinstance(self.selectString, str)):
            url = url + 'select=' + self.selectString + '&'
        # Adds the populateString
        if(isinstance(self.populateString, str)):
            url = url + 'populate=' + self.populateString + '&'

        return url

    def getChunkSize(self):
        firstChunk = None
        url = ''

        if isinstance(self.limitString, str) & isinstance(self.chunkSizeString, str):
            if int(self.chunkSizeString) >= int(self.limitString):
                firstChunk = self.limitString
            else:
                firstChunk = self.chunkSizeString

        if (isinstance(self.limitString, str)) & (not isinstance(self.chunkSizeString, str)):
            firstChunk = self.limitString

        if (not isinstance(self.limitString, str)) & (not isinstance(self.chunkSizeString, str)):
            firstChunk = self.chunkSizeString

        if(isinstance(firstChunk, str)):
            url = url + 'limit=' + firstChunk + '&'

        self.firstChunk = firstChunk
        return url

    def getTokenType(self):
        if len(self.token) > 32:
            return 'x-jwt-token'
        return 'x-token'

    def insertDataframe(self, df):
        data = df.to_dict(orient='records')

        for record in data:
            self.insert(record)

    def insert(self, data):
        if isinstance(data, pd.DataFrame):
            return self.insertDataframe(data)

        url = self.getQueryString()[:-1]
        tokenType = self.getTokenType()
        headers = {tokenType: self.token, 'content-type': 'application/json'}

        if 'data' not in data:
            data = {'data': data}

        try:
            response = requests.post(url, json=data, headers=headers)
        except Exception as e:
            print('Cannot insert data into the resource.')
            print(data)
            print(e)
            return

        return response

    def get(self):
        url = self.getQueryString() + self.getChunkSize()
        url = url[:-1]
        tokenType = self.getTokenType()

        try:
            firstResult = requests.get(url, headers={tokenType: self.token})
        except Exception as e:
            print('The query has an error or no results.')
            print(e)
            return []

        # textContent = firstResult.text
        # jsonContent = firstResult.json()

        return firstResult.json()

    def filter(self, filters):
        self.filterString = self.filterToString(filters)
        return self

    def select(self, select):
        self.selectString = self.selectToString(select)
        return self

    def limit(self, limit):
        self.limitString = str(limit)
        return self

    def populate(self, resources):
        self.populateString = self.populateToString(resources)
        return self

    def chunks(self, size):
        self.chunkSizeString = str(size)
        return self
