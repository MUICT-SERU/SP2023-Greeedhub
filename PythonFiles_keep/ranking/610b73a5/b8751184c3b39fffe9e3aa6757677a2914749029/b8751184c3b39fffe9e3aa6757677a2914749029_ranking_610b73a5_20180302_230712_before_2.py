import csv
import pandas as pd
import numpy as np


class Table(object):
    """ A Table object in rankit is equivalent to data. 
    It provides an interface to all ranking solutions in rankit.

    Table accepts <item1, item2, score1, score2> formatted input in pandas.dataframe/tsv/csv...
    """

    def __init__(self, data, col, weightcol=None, timecol=None, encoding="utf_8", delimiter='\t', hasheader=False):
        if len(col)!=4:
            raise ValueError("Parameter col must have four values, indicating columns for host, visit, host score and visit score.")
        if (not all(isinstance(i, str) for i in col)) and (not all(isinstance(i, int) for i in col)):
            raise ValueError("The type of col elements should be string or int.")
        if not isinstance(data, pd.DataFrame):
            raise ValueError("data should be pandas dataframe.")

        raw_table = data.iloc[:, col].copy() if all(isinstance(i, int) for i in col) else data.loc[:, col].copy()
        raw_table.columns = ["host", "visit", "hscore", "vscore"]
        raw_table.loc[:, ["hscore", "vscore"]] = raw_table.loc[:, ["hscore", "vscore"]].apply(pd.to_numeric)

        if weightcol is not None:
            raw_table['weight'] = data.iloc[:, weightcol].copy() if isinstance(weightcol, int) else data.loc[:, weightcol].copy()
        else:
            raw_table['weight'] = 1.0
        
        if timecol is not None:
            raw_table['time'] = data.iloc[:, timecol].copy() if isinstance(timecol, int) else data.loc[:, timecol].copy()

        itemlut = dict()
        indexlut = []
        idx = 0
        for row in raw_table.itertuples(index=False, name=None):
            if not row[0] in itemlut:
                itemlut[row[0]] = idx
                indexlut.append(row[0])
                idx+=1
            if not row[1] in itemlut:
                itemlut[row[1]] = idx
                indexlut.append(row[1])
                idx+=1

        self.itemlut = itemlut
        self.indexlut = indexlut
        self.itemnum = idx

        # raw table need to be converted to standard indexed table.
        raw_table['hidx'] = np.require(list(map(lambda x: itemlut[x], raw_table["host"].tolist())), dtype=np.int)
        raw_table['vidx'] = np.require(list(map(lambda x: itemlut[x], raw_table["visit"].tolist())), dtype=np.int)

        self.table = raw_table

    def getitemlist(self):
        return self.table.loc[:, ["host", "visit"]].copy()

    def _gettable(self):
        return self.table.loc[:, ["hidx", "vidx", "hscore", "vscore"]]
    
    def __repr__(self):
        return "Table with provided data:\n"+self.table[['host', 'visit', 'hscore', 'vscore']].__repr__()