# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import re
import difflib
from ast import literal_eval
from citableclass.base import Citable


class CorpusTextSearch(object):
    """
    This class is initialized with a searchstring, the name of the column,
    which contains the textstrings, and a path to a pickled dataframe.
    Optionally, a path to an excel file containing metadata can be provided.

    For other import formats change read_pickle and read_excel accordingly.

    Example:
            >>> search1 = CorpusTextSearch(
                            pathDF='/path/to/dataframe/file.xlsx',
                            dataType='excel',
                            dataIndex='single',
                            colname='main'
                            )

            >>> search1.reduce('date','1500').search('Thomas Morus').results()
            True
    """

    def __init__(
            self, pathDF,
            dataType='pickle', dataIndex='multi', colname='text',
            maxValues=2500, pathMeta=False, pathType=False
            ):

        self.datatype = dataType

        if pathType == 'DOI':
            pathDF = "http://dx.doi.org/{0}".format(pathDF)
        elif pathType == 'citable':
            self.citable = Citable(pathDF)
            self.dataframe = self.citable.digitalresource()
        elif pathType == 'citable-dev':
            self.citable = Citable(pathDF, formats='dev')
            self.dataframe = self.citable.digitalresource()
        elif pathType == 'citable-local':
            self.citable = Citable(pathDF, formats='local')
            self.dataframe = self.citable.digitalresource()
        elif pathType == 'variable':
            self.dataframe = pathDF

        if pathType not in ['variable', 'citable', 'citable-dev', 'citable-local']:
            if self.datatype == 'pickle':
                self.dataframe = pd.read_pickle(pathDF)
            elif self.datatype == 'excel':
                self.dataframe = pd.read_excel(pathDF)
            elif self.datatype == 'csv':
                self.dataframe = pd.read_csv(pathDF, error_bad_lines=False)
            elif self.datatype == 'json':
                self.dataframe = pd.read_json(pathDF)
            elif self.datatype == 'orientedJson':
                self.dataframe = pd.read_json(pathDF, orient='table')
            else:
                raise ValueError(
                    'Please provide data in pickle,excel,csv or json format'
                    )

        self.dataindex = dataIndex

        self.colValueDictTrigger = []
        if self.dataindex == 'single':
            for col in self.dataframe.columns:
                if not self.dataframe[col].dtype.name in ['int', 'int64', 'float64']:
                    try:
                        length = len(self.dataframe[col].unique())
                        if length < maxValues:
                            self.colValueDictTrigger.append(col)
                    except TypeError:
                        # print('Encountered list value in cell, skipping...')
                        pass
        elif self.dataindex == 'multi':
            for level in self.dataframe.index.names:
                if not self.dataframe.index.get_level_values(level).dtype.name in ['int', 'int64', 'float64']:
                    if len(self.dataframe.index.get_level_values(level).unique()) < maxValues:
                        self.colValueDictTrigger.append(level)
            for col in self.dataframe.columns:
                if not self.dataframe[col].dtype.name in ['int', 'int64', 'float64']:
                    try:
                        length = len(self.dataframe[col].unique())
                        if length < maxValues:
                            self.colValueDictTrigger.append(col)
                    except TypeError:
                        print('Encountered list value in cell, skipping...')
                        pass

        self.searchFields = []
        if self.dataindex == 'single':
            self.searchFields = self.dataframe.columns.tolist()
        elif self.dataindex == 'multi':
            self.searchFields = list(self.dataframe.index.names)
            self.searchFields.extend(self.dataframe.columns.tolist())

        self.extData = ''
        self.result = ''

        self.levelValues = {}

        self.column = colname

        if pathMeta:
            self.metaData = pd.read_excel(pathMeta)
        else:
            self.metaData = ''

    def resetColWidth(self):
        """ Reset pandas display option for max_colwidth"""
        pd.reset_option('display.max_colwidth')
        return

    def resetSearch(self):
        """Reset self.result to search in full dataframe again."""
        self.result = ''
        return

    def search(self, value):
        """
        Search string in 'colname' column.
        """
        if type(self.result) == str:
            self.result = self.dataframe[self.dataframe[self.column].str.contains(value)]
        elif isinstance(self.result, pd.DataFrame):
            self.result = self.result[self.result[self.column].str.contains(value)]
        return self

    def logicReduce(self, logicList):
        """
        Constructs complex searches for list of (part,value) tuples, connected
        via AND (&),OR (|),NOT (~&) logic. logicList has the format
        '[(part1,value1),&,(part2,value2),|,(part3,value3)]'.
        Evaluation is in order of apperance, e.g. for the above logicList,
        a boolean list is constructed for each (part,value) tuple.
        Then the first two tuples are compared with & yielding a temporary
        result temp1, which is compared with | with the last tuple.
        This creates a resulting boolean list res1,
        which is used to reduce the dataframe.
        """
        self.tempRes = []
        for part in logicList:
            if type(part) == tuple:
                res = self.boolList(part[0], part[1])
                self.tempRes.append(res)
            elif type(part) == str and part in ['&', '|', '~&']:
                self.tempRes.append(part)

        self.res = self.tempRes.pop(0)

        while self.tempRes:
            op = self.tempRes.pop(0)
            res2 = self.tempRes.pop(0)
            if op == '&':
                self.res = self.res & res2
            elif op == '|':
                self.res = self.res | res2
            elif op == '~&':
                self.res = self.res & np.invert(res2)
            else:
                pass

        if type(self.res) != str:
            self.result = self.dataframe[self.res]
        return self

    def boolList(self, level, value):
        """ Returns boolean list for dataframe[part]==value."""
        try:
            values = literal_eval(value)
            assert type(values) == list
            value = values
        except:
            pass
        if type(value) != list:
            if any([x in value for x in ['<', '>', '<=', '>=']]):
                for x in ['<=', '>=', '<', '>']:
                    if x in value:
                        logicSymbol = x
                        parts = [x.strip() for x in value.split(logicSymbol)]
                        if len(parts) == 3:
                            if logicSymbol == '<':
                                res = self.dataframe[level].astype(float).between(int(parts[0]), int(parts[-1]), inclusive=False)
                            elif logicSymbol == '<=':
                                res = self.dataframe[level].astype(float).between(int(parts[0]), int(parts[-1]))
                            else:
                                raise ValueError('Cannot understand boundaries. Aborting..')
                        else:
                            if logicSymbol == '<':
                                res = self.dataframe[level].astype(float).lt(int(parts[-1]))
                            elif logicSymbol == '<=':
                                res = self.dataframe[level].astype(float).le(int(parts[-1]))
                            elif logicSymbol == '>':
                                res = self.dataframe[level].astype(float).gt(int(parts[-1]))
                            elif logicSymbol == '>=':
                                res = self.dataframe[level].astype(float).ge(int(parts[-1]))
                            else:
                                raise ValueError('Cannot understand boundaries. Aborting..')
                        return res
            else:
                searchvalue = self._fuzzySearch(level, value)
                if self.dataindex == 'multi' and level != self.column:
                    try:
                        res = self.dataframe.index.get_level_values(level) == self._assertDataType(level, searchvalue, self.dataframe)
                    except:
                        res = self.dataframe[level] == self._assertDataType(level, searchvalue, self.dataframe)
                elif self.dataindex == 'single' and level != self.column:
                    res = self.dataframe[level] == self._assertDataType(level, searchvalue, self.dataframe)
                    if not any(res):
                        try:
                            res = self.dataframe[level].apply(lambda row: any([value in x for x in self._yieldListElem(row)]))
                        except:
                            pass
                elif level == self.column:
                    res = self.dataframe[level].str.contains(self._assertDataType(level, value, self.dataframe)) == True
            return res
        else:
            if self.dataindex == 'multi':
                mask = self.dataframe.index.get_level_values(level).isin(values)
            else:
                mask = self.dataframe[level].isin(values)
            return mask

    def _yieldListElem(self, inList):
        for y in inList:
            if isinstance(y, list):
                yield from self._yieldListElem(y)
            else:
                yield y

    def _fuzzySearch(self, level, value):
        """
        Allow fuzzy search for reduce() and search() routines. Limited to
        columns in the colValueDictTrigger list. This excludes columns containing
        numerical or list data, as well as the main column 'colname'.
        """
        if level in self.colValueDictTrigger and level != self.column:
            if level not in self.levelValues.keys():
                if self.dataindex == 'multi':
                    try:
                        self.levelValues[level] = [str(x) for x in self.dataframe.index.get_level_values(level).unique()]
                    except:
                        self.levelValues[level] = [str(x) for x in self.dataframe[level].unique()]
                elif self.dataindex == 'single':
                    self.levelValues[level] = [str(x) for x in self.dataframe[level].unique()]
                else:
                    raise ValueError(
                        'DataIndex not "single" or "multi".'
                        )
            else:
                pass

            if value not in self.levelValues[level]:
                try:
                    closestMatch = difflib.get_close_matches(value, self.levelValues[level], 1)
                    if closestMatch:
                        searchValue = closestMatch[0]
                    else:
                        searchValue = value
                        print(
                            'Could not find matching expression to search.'
                            )
                except TypeError:
                    searchValue = value
            else:
                searchValue = value
        else:
            searchValue = value
        return searchValue

    def reduce(self, level, value):
        """ Return reduced dataframe for search tuple (level/column,value):
            a) as cross-section for multi-index dataframe:
               df.xs(value,level=level)
            b) as sub-dataframe for single-index dataframe:
               df[df.column == value]

            Result is in self.result, to be able to chain reductions.
            To view result use self.results()
        """
        try:
            values = literal_eval(value)
            assert type(values) == list
            value = values
        except:
            pass
        if type(value) == list:
            searchValues = [self._fuzzySearch(level, val) for val in value]
            self._searchValues(level, searchValues)
        else:
            searchValue = self._fuzzySearch(level, value)
            self._searchString(level, searchValue)
        return self

    def _searchValues(self, level, values):
        """Helper function to slice dataframe with a list of values"""
        if self.dataindex == 'multi':
            if type(self.result) == str:
                mask = self.dataframe.index.get_level_values(level).isin(values)
                self.result = self.dataframe[mask]
            else:
                mask = self.result.index.get_level_values(level).isin(values)
                self.result = self.result[mask]
        else:
            if type(self.result) == str:
                self.result = self.dataframe[self.dataframe[level].isin(values)]
            else:
                self.result = self.result[self.result[level].isin(values)]

    def _searchString(self, level, value):
        """Helper function for reducing dataframes"""
        if self.dataindex == 'multi':
            if type(self.result) == str:
                try:
                    self.result = self.dataframe.xs(self._assertDataType(level, value, self.dataframe), level=level, drop_level=False)
                except:
                    self.result = self.dataframe[self.dataframe[level] == self._assertDataType(level, value, self.dataframe)]
            else:
                try:
                    self.result = self.result.xs(self._assertDataType(level, value, self.result), level=level, drop_level=False)
                except:
                    self.result = self.result[self.result[level] == self._assertDataType(level, value, self.result)]
        elif self.dataindex == 'single':
            if type(self.result) == str:
                self.result = self.dataframe[self.dataframe[level] == self._assertDataType(level, value, self.dataframe)]
            else:
                self.result = self.result[self.result[level] == self._assertDataType(level, value, self.result)]

    def _assertDataType(self, level, value, dataframe):
        """Helper function to assert correct datatype for value at level or in column"""
        numTypes = ['int8', 'int16', 'int32', 'int64', 'float', 'float64']
        valueType = type(value)
        if self.dataindex == 'multi' and level != self.column:
            try:
                levelType = self.dataframe.index.get_level_values(level=level).dtype.name
            except:
                levelType = self.dataframe[level].dtype.name
        elif self.dataindex == 'single' or level == self.column:
            levelType = self.dataframe[level].dtype.name
        if levelType == 'object' and valueType == str:
            return value
        elif levelType == 'object' and valueType == int:
            try:
                return str(value)
            except ValueError as err:
                raise('Can not cast {0} to type {1}'.format(value, levelType))
        elif levelType in numTypes and valueType == int:
            return value
        elif levelType in numTypes and valueType == float:
            return value
        elif levelType in numTypes and valueType == str:
            try:
                return int(value)
            except ValueError:
                raise ValueError('Can not cast {0} to type {1}'.format(value, levelType))
        else:
            raise ValueError('Can not cast {0} to type {1}'.format(value, levelType))

    def results(self):
        """Returns the search result as a single-index dataframe."""
        if self.dataindex == 'multi':
            self.indexLevels = list(self.result.index.names)
            formatedResult = self.result.reset_index(level=self.indexLevels)
        elif self.dataindex == 'single':
            formatedResult = self.result
        pd.set_option('display.max_colwidth', -1)
        return formatedResult

    def extResults(self, level):
        """
        Returns the search result as a single-index dataframe, extend with
        metadata on the desired level. The metadata is calculated for all other
        levels of multi-indexed dataframe.
        """
        # TODO: Add statistics for single-level dataframes.
        if not self.dataindex == 'multi':
            print('Statistics for multiindexed dataframes only.')
            return
        self.extData = pd.merge(left=self.results(), right=self._metaData(level), on=level)
        cols = [x for x in self.extData.columns if x != self.column]
        cols = cols + [self.column]
        self.extData = self.extData[cols]
        pd.set_option('display.max_colwidth', -1)
        return self.extData

    def _countWords(self, level, value):
        """Helper function to count words on a given level."""
        text = ' '.join([str(x) for x in self.dataframe.xs(value, level=level).text.tolist()])
        numWords = len(re.findall(r'\w+', text))
        return numWords

    def _getStatistics(self, level):
        """Helper function to return statistics on given level."""
        retDict = {}
        subLevels = self.indexLevels.copy()
        try:
            subLevels.remove(level)
        except ValueError:
            print('{0} not in index'.format(level))

        for part in self.dataframe.index.get_level_values(level).unique():
            partDict = {}
            for subLevel in subLevels:
                num = len(self.dataframe.xs(part, level=level).index.get_level_values(subLevel).unique())
                if num > 1:
                    partDict['Num_' + subLevel] = num
            partDict['words'] = self._countWords(level, part)
            retDict[part] = partDict
        return retDict

    def _metaData(self, level):
        """Helper function to generate dataframe from statistics."""
        resDict = self._getStatistics(level)
        self.metaDataFrame = pd.DataFrame(resDict).fillna('1').astype('int').transpose().reset_index().rename({'index': level}, axis=1)
        return self.metaDataFrame
