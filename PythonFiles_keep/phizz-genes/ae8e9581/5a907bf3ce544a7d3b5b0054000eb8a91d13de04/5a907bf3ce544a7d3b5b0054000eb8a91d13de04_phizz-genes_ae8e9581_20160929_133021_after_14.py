from __future__ import unicode_literals

from django.db import models

class Gene(models.Model):
    
    #The ensembl gene id, ex. 'ENSG00000156110'
    #can be use with link like:
    #ensembl.org/Homo_sapiens/Gene/Summary?g=ENSG00000156110
    ensembl_id = models.CharField(max_length=20)

    chrom = models.CharField(max_length=30)
    start = models.IntegerField()
    stop = models.IntegerField()
    
    #The hgnc symbol, ex. 'ADK
    hgnc_symbol = models.CharField(max_length=20, blank=True)
    
    description = models.CharField(max_length=200, null=True)
    #The hgnc id, ex. '257' for using link like:
    #genenames.org/cgi-bin/gene_symbol_report?hgnc_id=HGNC:257
    hgnc_id = models.IntegerField(null=True)
    
    #entrez id, ex. 132, for using link like:
    #ncbi.nlm.nih.gov/gene/132
    entrez_id = models.IntegerField(null=True)
    
    #vega id, ex. OTTHUMG00000018506, for using link like:
    #http://vega.sanger.ac.uk/Homo_sapiens/Gene/Summary?db=core;g=OTTHUMG00000018506
    vega_id = models.CharField(max_length=20, null=True)
    
    #ucsc id, ex. uc001jwi.4, for using link like:
    #http://genome.cse.ucsc.edu/cgi-bin/hgGene?org=Human&hgg_chrom=none&hgg_type=knownGene&hgg_gene=uc001jwi.4
    ucsc_id = models.CharField(max_length=20, null=True)
    
    #pli_score is the estimated sensibility to lof mutations estimated by ExAC
    pli_score = models.DecimalField(max_digits=6, decimal_places=5, null=True)
    
    def __str__(self):
        return self.hgnc_symbol

#One gene can have several transcripts, one transcript are attached to one gene
class Transcript(models.Model):
    gene = models.ForeignKey(Gene, on_delete=models.CASCADE)
    refseq_name = models.CharField(max_length=30, null=True)
    ensembl_transcript_id = models.CharField(max_length=30)
    
    def __str__(self):
        return self.refseq_name

#One phenotype can have several transcripts, one transcript are attached to one gene
class Omim(models.Model):
    gene = models.ForeignKey(Gene, on_delete=models.CASCADE)
    omim_id = models.IntegerField()

class Alias(models.Model):
    gene = models.ForeignKey(Gene, on_delete=models.CASCADE)
    alias = models.CharField(max_length=20)

class UniProt(models.Model):
    gene = models.ForeignKey(Gene, on_delete=models.CASCADE)
    uniprot_id = models.CharField(max_length=20)
    
    