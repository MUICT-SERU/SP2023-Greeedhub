from django.test import TestCase

from .models import (Gene,Alias, Transcript, Omim)

class DatabaseOperationTests(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        cls.gene_one = Gene.objects.create(
            ensembl_id = 'ENSG00000156110',
            hgnc_symbol = 'ADK',
            chrom = '10',
            start = 75910960,
            stop = 76469061,
        )
        
        #Create an alias
        cls.alias = Alias.objects.create(
            gene = cls.gene_one,
            alias = 'ADK1',
        )

        #Create an transcript
        cls.transcript = Transcript.objects.create(
            gene = cls.gene_one,
            refseq_name = 'NM_1',
            ensembl_transcript_id = 'ENST001'
        )
        
        cls.omim = Omim.objects.create(
            gene = cls.gene_one,
            omim_id = '1'
        )
    
    def test_gene(self):
        self.assertEqual(self.gene_one.hgnc_symbol, 'ADK')
    
    def test_alias(self):
        gene = Gene.objects.get(hgnc_symbol='ADK')
        self.assertTrue(self.alias in gene.alias_set.all())

    def test_transcripts(self):
        gene = Gene.objects.get(hgnc_symbol='ADK')
        self.assertTrue(self.transcript in gene.transcript_set.all())

    def test_omim(self):
        gene = Gene.objects.get(hgnc_symbol='ADK')
        self.assertTrue(self.omim in gene.omim_set.all())
        
        