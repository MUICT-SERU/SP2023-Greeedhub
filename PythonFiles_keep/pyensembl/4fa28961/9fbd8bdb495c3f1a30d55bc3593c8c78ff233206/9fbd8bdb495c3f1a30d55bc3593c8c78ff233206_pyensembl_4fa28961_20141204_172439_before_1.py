from locus import Locus

import numpy as np

class Exon(Locus):
    def __init__(self, exon_id, db):

        if not isinstance(exon_id, (unicode, str)):
            raise TypeError(
                "Expected exon ID to be string, got %s : %s" % (
                    exon_id, type(exon_id)))

        self.id = exon_id
        self.db = db

        columns = [
            'seqname',
            'start',
            'end',
            'strand',
            'gene_name',
            'gene_id',
        ]
        columns_str = ", ".join(columns)

        query = """
            SELECT %s
            FROM ensembl
            WHERE exon_id = ?
            AND feature='exon'
        """ % columns_str

        cursor = db.execute(query, [exon_id])

        # exon IDs are unique, so should be either 0 or 1 results
        results = cursor.fetchall()

        if len(results) == 0:
            raise ValueError("Exon ID not found: %s" % exon_id)

        assert len(results) == 1
        result = results[0]

        result_dict = {}
        for i, column_name in enumerate(columns):
            result_dict[column_name] = result[i]

        Locus.__init__(
            self,
            result_dict['seqname'],
            result_dict['start'],
            result_dict['end'],
            result_dict['strand'])

        self.gene_name = result_dict['gene_name']
        self.gene_id = result_dict['gene_id']


    def __str__(self):
        return "Exon(exon_id=%s, gene_name=%s)" % (self.id, self.gene_name)

    def __repr__(self):
        return str(self)

    # possible annotations associated with exons
    _EXON_FEATURES = {'start_codon', 'stop_codon', 'UTR', 'CDS'}

    def _query_exon_feature_locations(self, feature, required=False):
        if feature not in self._EXON_FEATURES:
            raise ValueError("Invalid exon feature: %s" % feature)

        query = """
            SELECT seqname, start, end, strand
            FROM ensembl
            WHERE feature= ?
            AND exon_id = ?
        """
        cursor = self.db.execute(query, [feature, self.id])
        results = cursor.fetchall()
        if required and len(results) == 0:
            raise ValueError(
                "Exon %s does not contain feature %s" % (self.id, feature))
        return results


    @property
    def contains_start_codon(self):
        """
        Does this exon contain a start codon?
        """
        if not hasattr(self, "_contains_start_codon"):
            results = self._query_exon_feature_locations('start_codon')
            self._contains_start_codon = len(results) > 0
        return self._contains_start_codon

    @property
    def contains_stop_codon(self):
        """
        Does this exon contain a stop codon ?
        """
        if not hasattr(self, "_contains_stop_codon"):
            results = self._query_exon_feature_locations('stop_codon')
            self._contains_stop_codon = len(results) > 0
        return self._contains_stop_codon


    def _feature_offset(self, feature):
        """
        Return the position of feature (e.g. start_codon) in
        coordinates relative to the start of this exon.
        """

        results = self._query_exon_feature_locations(feature)

        # in case there are multiple results, choose the
        # first, which is either a higher or lower position depending
        # on the strand. Since start/end ignore the strand (start always
        # less than end), we need to look at both to determine which
        # position is "first" on the strand.
        positions = []
        for entry in results:
            seqname, start, end, strand = entry
            assert seqname == self.contig, \
                "Wrong contig for exon: %s (should be %s)" % (
                    seqname, self.contig)
            assert strand in ("+", "-"), "Invalid strand: %s" % strand
            assert strand == self.strand, \
                "Wrong strand on %s, expected %s but got %s" % (
                    feature, self.strand, strand)
            assert isinstance(position, (int,long)), \
                "Invalid type %s for position %s" % (type(position), position)
            positions.append(start)
            positions.append(end)

        if self.on_forward_strand:
            first_position = min(positions)
        else:
            first_position = max(positions)

        local_position = self.position_offset(earliest_position)

        if local_position < 0:
            raise ValueError(
                "%s starts before exon %s" % (feature, self.id))

        return local_position

    @property
    def start_codon_offset(self):
        """
        How many bases from the beginning of the exon (starting from 0)
        is the first base of the start codon?
        """
        return self._feature_offset('start_codon')


    @property
    def stop_codon_offset(self):
        """
        How many bases from the beginning of the exon (starting from 0)
        is the first base of the stop codon?
        """
        return self._feature_offset("stop_codon")

