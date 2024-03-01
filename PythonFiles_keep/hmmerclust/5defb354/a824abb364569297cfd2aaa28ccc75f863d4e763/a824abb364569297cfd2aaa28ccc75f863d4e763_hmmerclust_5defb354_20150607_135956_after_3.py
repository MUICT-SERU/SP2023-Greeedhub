from Bio import SeqIO, SearchIO
import subprocess
from multiprocessing import cpu_count
from collections import OrderedDict
from pandas import DataFrame
import pprint
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import pylab
from random import random
import os

processors = cpu_count()

def test():
    print 'test'


class OrganismDB:
    
    """ 
    Recieves a list of genomes,
    Makes a list of seqRecord objects,
    Generates a list of Organism objects.
    
    """
    
    def __init__(self, database_name, genome_list, genome_dir, freshfasta=False, search=None):

        self.database_name = database_name
        self.genome_list = genome_list
        self.genome_dir = genome_dir
        self.combined_proteome_file_name = None

        if freshfasta==True:
            self.generate_combined_fasta(self.genome_list, self.genome_dir)

        self.organisms = [] #self.make_organisms(self.seq_record_list)
        #self.seq_record_list = self.make_seq_record(self.genome_list, self.genome_dir)
        self.search = search
        self.df = None
        self.group_dict = None
        self.make_organisms(self.genome_list, self.genome_dir)
        self.rRNA16SDB = rRNA16SDB(self)

    def generate_combined_fasta(self, genome_list, genome_dir):

        fasta = []
            
        for genome in genome_list:
            
            full_path = genome_dir + genome
            handle = open(full_path, "rU")
            print 'making combined fasta for', genome
            try:
                seq_record = SeqIO.read(handle, 'genbank')
                org_accession = seq_record.name
                
            except AssertionError,e:
                print str(e), genome
                        
            for feature in seq_record.features:
                if feature.type == 'CDS':
                    try:                                  
                        prot_accession = feature.qualifiers['protein_id'][0]
                        prot_translation = feature.qualifiers['translation'][0]
                        
                        newfast = '>' + org_accession + ',' + prot_accession + \
                         '\n' + prot_translation + '\n'
                        
                        #if newfast not in fasta:
                        fasta.append(newfast)
                            
                    except AttributeError,e:
                        print "organism %s, protein %s did not have \
                        the right attributes" % (org_accession, prot_accession)
                        print str(e)
                    
                    except KeyError,e:
                        print "organism %s, protein %s did not have \
                        the right key" % (org_accession, prot_accession)
                        print str(e)
                          
            handle.close()
            
            print "%s proteins were added" % len(fasta)

            set_fasta = set(fasta)

            print "%s unique proteins were added -- dropping redundant ones" % len(set_fasta)
                                                
        faastring = "".join(set_fasta)

        write_fasta = open('combined_fasta', 'w')
        write_fasta.write(faastring)
        write_fasta.close()

        return set_fasta

    def make_organisms(self, genome_list, genome_dir): 

        for genome in genome_list:

            genome_path = genome_dir + genome
            handle = open(genome_path, "rU")
            print 'Adding organism attributes for', genome

            try:
                seq_record = SeqIO.read(handle, "genbank")

                self.organisms.append(Organism(seq_record, genome_path, self))

                del(seq_record)

            except ValueError,e:
                print genome, str(e)

            except AssertionError,e:
                print genome, str(e)

            except UnboundLocalError,e:
                print genome, str(e)

            handle.close()

    def add_protein_to_organisms(self, orgprot_list):

        '''
        Takes a list of items in org_acc, prot_acc,
        e.g. NC_015758,YP_004723756.1,
        adds to the

        '''

        for org in self.organisms:

            handle = open(org.genome_path, "rU")
            print 'adding proteins to organism', org.accession
            try:
                seq_record = SeqIO.read(handle, "genbank")

                feature_list = []

                for id in orgprot_list:
                    org_id = id.split(',')[0]
                    prot_id = id.split(',')[1]

                    if org.accession == org_id:
                        for feature in seq_record.features:
                            if feature.type == 'CDS':
                                feat_prot_acc = feature.qualifiers['protein_id'][0]
                                if feat_prot_acc == prot_id:
                                    #print 'appending', hit_prot_acc
                                    org.proteins.append(Protein(feature))

                del(seq_record)

            except ValueError,e:
                print 'error for ', org.accession, str(e)

            except AssertionError,e:
                print 'error for ', org.accession, str(e)

            except UnboundLocalError,e:
                print 'error for ', org.accession, str(e)

            except KeyError,e:
                print 'error for ', org.accession, str(e)

            handle.close()

    def add_hits_to_proteins(self, hmm_hit_list):

        for org in self.organisms:
            print "adding SearchIO hit objects for", org.accession

            for hit in hmm_hit_list:
                hit_org_id = hit.id.split(',')[0]
                hit_prot_id = hit.id.split(',')[1]

                if org.accession == hit_org_id:
                    for prot in org.proteins:
                        if prot.accession == hit_prot_id:
                            prot.hmm_hit_list.append(hit)


    def cluster_number(self, data, maxgap):    
        data.sort()
        groups = [[data[0]]]
        for x in data[1:]:
            if abs(x - groups[-1][-1]) <= maxgap:
                groups[-1].append(x)
            else:
                groups.append([x])
        return groups

    def find_loci(self, cluster_size, maxgap, locusview=False, colordict=None, required=None):
        
        '''
        Pass the minimum number of locus members, the maximum basepair
        gap between members.

        kwargs:
        locusview: whether or not a map is generated for the locus_parent_organism
        colordict: pass a pre-made color scheme for identified proteins
        required: a list of hits the locus must

        '''

        if colordict != None:
            self.search.protein_arrow_color_dict = colordict        

        for organism in self.organisms:

            print 'finding loci for', organism.name

            #reset loci if there is something in there already
            organism.loci = []
            
            orghits = []
            for protein in organism.proteins:
                if len(protein.hmm_hit_list) > 0:
                    orghits.append((organism.accession, protein.accession, 
                                    protein.start_bp, protein.end_bp, protein))
            
            bp_start_pooled = [hit[2] for hit in orghits]  
            
            try:
                clustered_data = self.cluster_number(bp_start_pooled, maxgap)
            
                significant_cluster_list = []
                for cluster in clustered_data:
                    if len(cluster) > cluster_size:
                        significant_cluster_list.append(cluster)

                #print significant_cluster_list
                
                for cluster in significant_cluster_list:
                    proteins_in_locus = []
                    cluster.sort()
                    for bp_start in cluster:
                        for hit in orghits:
                            if bp_start == hit[2]:
                                proteins_in_locus.append(hit[4])
                    
                    organism.loci.append(Locus(proteins_in_locus, 
                                               organism, 
                                               self.search.query_names, 
                                               locusview))

            except IndexError,e:
                print 'Index error', str(e), organism.name

            print 'total of', str(len(organism.loci)), 'found for', organism.name

    def clear_loci():
        for org in self.organisms:
            org.loci=None

class Organism(object):
    
    """
    Encapsulates data related to a single organism.

    Args:
        seq_record (SeqRecord): biopython seqrecord object
        genome_path (str): The path to genome 
        OrganismDB (OrganismDB): the parent organism database

    Attributes:
        genome_path (str)
        parent_db (OrganismDB)
        


    """
    
    def __init__(self, seq_record, genome_path, OrganismDB):
        
        self.genome_path = genome_path
        self.parent_db = OrganismDB
        self.accesion_version = seq_record.id
        self.accession = seq_record.name
        self.description = seq_record.description
        self.name = seq_record.annotations['source']
        self.taxonomy = seq_record.annotations['taxonomy']
        self.species = " ".join(self.name.split(" ")[0:2])
        try:
            self.kingdom = self.taxonomy[0]
            self.phylum = self.taxonomy[1]
            self.clazz = self.taxonomy[2]
            self.order = self.taxonomy[3]
            self.family = self.taxonomy[4] 
            self.genus = self.taxonomy[5]
        except:
            print 'Unable to parse taxonomy for', self.accession
            self.taxonomy = None
            self.kingdom = None
            self.phylum = None
            self.clazz = None
            self.order = None
            self.family = None
            self.genus = None

        self.rRNA16S_sequence = None
        self.tree_order = 0

        self.proteins = []

        self.genome_length = len(seq_record.seq)
        #self.proteome = Proteome(hit_features_only)
        #self.seq_record = seq_record
        self.loci = []  # list of Locus objects

class Proteome:
    
    '''
    Takes a seq_record_features object

    An object representing all the proteins from an Organism.
    Has Protein objects.
    
    Can generate a FASTA that can be queried by hmmsearch

    A Proteome belongs to an Organism
    '''
    
    def __init__(self, seq_record_features):
        
        #self.seq_record_features = seq_record_features
        self.proteins = []
        self.protein_count = len(self.proteins)
        self.generate_proteome(seq_record_features)
        
    def generate_proteome(self, seq_record_features):
        for feature in seq_record_features:
            if feature.type == 'CDS':
                self.proteins.append(Protein(feature))

class Protein:
    
    """
    Takes a SeqIO feature object

    An object representing an indiviudual CDS from the Organism
    
    With the data we care about

    """
    
    def __init__(self, feature):    


        #self.seqrecord_feature = feature
        self.accession = feature.qualifiers['protein_id'][0]
        self.gi = feature.qualifiers['db_xref'][0].split(':')[1]
        self.product = feature.qualifiers['product'][0]
        #self.note = feature.qualifiers['note']
        self.start_bp = feature.location.start.position
        self.end_bp = feature.location.end.position
        self.strand = feature.location.strand
        self.translation = feature.qualifiers['translation'][0]
        self.numb_residues = len(self.translation)

        self.hmm_hit_list = []
        self.hit_dataframe = None
        self.hit_name_best = 'non-hit'
        self.hit_evalue_best = 'non-hit'
        self.hit_bitscore_best = 'non-hit'
        self.hit_bias_best = 'non-hit'
        self.hit_start_best = 'non-hit'
        self.hit_end_best = 'non-hit'

        self.is_in_locus = None

    def __repr__(self):
        return "%s - %s" % (self.accession, self.product)


    def parse_hmm_hit_list(self, hmm_hit_list):

        '''
        take a list of hmm hit results, take needed info,

        '''

        tuplist = []

        for hit in hmm_hit_list:
            for hsp in hit.hsps:
                tup = tuplist.append((hit._query_id.split('_')[0],
                                     hit.bitscore,
                                     hit.evalue,
                                     hsp.bias,
                                     hsp.env_start,
                                     hsp.env_end))
    
        cols = ['name','bitscore','evalue', 'bias', 'hsp_start','hsp_end']
            
        df = DataFrame(tuplist, columns=cols)
        df.set_index('name', inplace=True)
        return df

class rRNA16SDB:

    def __init__(self, OrganismDB):

        #self.write_16S_rRNA_fasta(OrganismDB.organisms)
        self.import_tree_order_from_file(OrganismDB, '16S_aligned.csv')


    def write_16S_rRNA_fasta(self, org_list):

        '''
        Writes a fasta file containing 16S rRNA sequences
        for a list of Organism objects,

        The first 16S sequence found in the seq record object is used,
        since it looks like there are duplicates
        '''

        fasta = []
        for org in org_list:

            handle = open(org.genome_path, "rU")


            seq_record = SeqIO.read(handle, "genbank")

            for feat in seq_record.features:
                if feat.type == 'rRNA':
                    if '16S ribosomal' in feat.qualifiers['product'][0]:
                        start = feat.location.start.position
                        end = feat.location.end.position

                        if ((end - start) > 1400) & ((end - start) < 1700) :

                            print 'rRNA sequence extracted for', org.accession

                            fasta.append('>' + org.accession +
                                         '\n' + 
                                         str(feat.extract(seq_record.seq)) +
                                          '\n')

                            org.rRNA16S_sequence = str(feat.extract(seq_record.seq))
                            
                            break

                    
        faastring = "".join(fasta)
        filename = '16S-rRNA.fasta'
        write_fasta = open(filename, 'w')
        write_fasta.write(faastring)
        write_fasta.close()


    def import_tree_order_from_file(self, MyOrganismDB, filename):

        '''
        Import the accession list that has been ordered by position
        in a phylogenetic tree. Get the index in the list, and
        add this to the Organism object. Later we can use this position
        to make a heatmap that matches up to a phylogenetic tree.
        '''
       
        tree_order = [acc.strip() for acc in open(filename)]
        #print tree_order

        for org in MyOrganismDB.organisms:
            for tree_accession in tree_order:
                #print tree_accession
                if org.accession == tree_accession:
                    org.tree_order = tree_order.index(tree_accession)


class HmmSearch:
    
    """
    Give alignment files, name them according to what the names
    should be in the analysis.

    First the hmm is built with Hmmbuild, and the hmm files output.

    Then run Hmmsearch, parse the files, put each result in a list

    """
    
    def __init__(self, OrganismDB, combined_fasta, freshbuild=True, freshsearch=True, ):
        
        self.alignment_dir = './alignments/'
        self.alignment_list = [x for x in os.listdir(self.alignment_dir) if '.txt' in x]
        self.query_names = []

        self.hmm_dir = './hmm/'
        if not os.path.exists(self.hmm_dir):
            os.makedirs(self.hmm_dir)

        self.combined_fasta = combined_fasta

        self.hhsearch_result_folder = './hhsearch_results/'
        if not os.path.exists(self.hhsearch_result_folder):
            os.makedirs(self.hhsearch_result_folder)

        self.hmm_result_list=[]

        if freshbuild == True:
            self.run_hmmbuild()

        if freshsearch == True:
            self.run_hmmsearch()

        self.combined_hit_list = self.extract_hit_list_from_hmmsearch_results()

        self.orgprot_list =  list(set([x.id for x in self.combined_hit_list]))

        OrganismDB.search = self

        self.protein_arrow_color_dict = self.make_protein_arrow_color_dict(self.query_names)

        OrganismDB.add_protein_to_organisms(self.orgprot_list)
        OrganismDB.add_hits_to_proteins(self.combined_hit_list)
        self.parse_proteins(OrganismDB)
        self.set_best_hit_values_for_proteins(OrganismDB)

    def run_hmmbuild(self):

        '''
        Generate hmm with hhbuild,
        output to file. Also stores query names.
        '''

        for alignment in self.alignment_list:

            print 'building Hmm for', alignment

            alignment_full_path = self.alignment_dir + alignment
            query_name = alignment.split("_")[0]
            self.query_names.append(query_name)

            new_hmm= self.hmm_dir + query_name + ".hmm"

            hmmbuild_output = subprocess.call(["hmmbuild", new_hmm,
             alignment_full_path])

        print 'hhbuild complete for', self.query_names

    def run_hmmsearch(self):

        '''
        
        '''
  
        all_searches = []

        for name in self.query_names:

            print 'running HHsearch on', name

            hmm_full_path = self.hmm_dir + name + '.hmm'
            hmmsearch_output = subprocess.check_output(["hmmsearch",
             "--cpu", str(processors), hmm_full_path,
              self.combined_fasta])

            hmm_result_file_name = self.hhsearch_result_folder + name + ".out"

            self.hmm_result_list.append((name + ".out"))

            f = open(hmm_result_file_name, 'w')
            f.write(hmmsearch_output)
            f.close()


    def extract_hit_list_from_hmmsearch_results(self):

        '''
        Make a giant list of all the hit objects from
        our search
        '''

        combined_list_of_hits = []

        for result in self.hmm_result_list:
            fullpath = self.hhsearch_result_folder + result
            

            se = SearchIO.read(fullpath, 'hmmer3-text')

            sublist = []
            for hit in se:
                combined_list_of_hits.append(hit)
                sublist.append(hit.id)
            print 'extracted', str(len(sublist)), 'hits for', result
            
        return combined_list_of_hits  


    def make_protein_arrow_color_dict(self, query_names):

        '''
        Generates a random color for all proteins in query_names,
        stores these in a dict.
        '''

        protein_arrow_color_dict = dict()

        for protein in self.query_names:
            protein_arrow_color_dict[protein] = (random(), random(), random())

        return protein_arrow_color_dict


    def make_hsps(self, hit):
        
        hit_name = hit._query_id.split("_")[0]
        hit_evalue = hit.evalue
        hit_bitscore = hit.bitscore


    def parse_proteins(self,OrganismDB):

        '''
        Iterate through all the proteins in the DB,
        creates a hit_dataframe for each protein.
        '''

        for org in OrganismDB.organisms:
            for prot in org.proteins:
                if len(prot.hmm_hit_list) > 0:
                    try:
                        prot.hit_dataframe = prot.parse_hmm_hit_list(prot.hmm_hit_list)
                    except ValueError,e:
                        print 'error for', org.name, prot.accession, str(e)

    def set_best_hit_values_for_proteins(self, OrganismDB):

        '''
        Iterate through all proteins in the DB,
        drop duplicates in the hit_dataframe, then store the maximum
        hit information as protein attributes.
        '''

        for org in OrganismDB.organisms:
            print 'setting best hit values for', org.name
            for prot in org.proteins:
                if len(prot.hmm_hit_list) > 0:
                    try:
                        dd_df = prot.hit_dataframe.drop_duplicates(subset='bitscore')
                        try:
                            prot.hit_name_best = dd_df.bitscore.idxmax()
                            prot.hit_evalue_best = dd_df.ix[prot.hit_name_best].evalue
                            prot.hit_bitscore_best = dd_df.ix[prot.hit_name_best].bitscore
                            prot.hit_bias_best = dd_df.ix[prot.hit_name_best].bias
                            prot.hit_start_best = dd_df.ix[prot.hit_name_best].hsp_start
                            prot.hit_end_best = dd_df.ix[prot.hit_name_best].hsp_end
                        except:
                            print 'could not set best hit values for ', org.name

                    except AttributeError:
                        pass

class Locus:

    '''
    Accepts list of protein objects, typically clustered proteins
    generated by the find_loci() method. The first and last proteinsin in
    the locus are defined as boundaries
    Also add the Locus back to the OrganismDB

    '''
    
    def __init__(self, list_of_protein_objects, organism, query_proteins, locusview):

        self.locus_hit_membership = list_of_protein_objects

        for prot in self.locus_hit_membership:
            prot.is_in_locus = self

        self.locus_number_of_hits = len(self.locus_hit_membership)
        self.locus_min_hit_boundary = self.locus_hit_membership[0].start_bp
        self.locus_max_hit_boundary = self.locus_hit_membership[-1].end_bp
        self.locus_bp_size = int(self.locus_hit_membership[-1].end_bp) - \
        int(self.locus_hit_membership[0].start_bp)
        self.locus_total_membership = self.get_total_membership(organism)
        self.locus_number_in_total = len(self.locus_total_membership)
        self.query_proteins = query_proteins
        self.locus_parent_organism = organism

        #print organism.proteome.proteins

        if locusview == True:
            LocusView(self)

        self.write_out_locus_fasta()

    def get_total_membership(self, organism):

        handle = open(organism.genome_path, "rU")
        total_membership_list = list(self.locus_hit_membership)

        try: 
            seq_record = SeqIO.read(handle, "genbank")

            for feature in seq_record.features:
                if feature.type == 'CDS':

                    locus_hit_accs = [x.accession for x in self.locus_hit_membership]
                    if feature.qualifiers['protein_id'][0] not in locus_hit_accs:

                        featstart = feature.location.start.position
                        featend = feature.location.end.position

                        if ((featstart >= self.locus_min_hit_boundary) and
                         (featend <= self.locus_max_hit_boundary)):

                            newprot = (Protein(feature))

                            newprot.is_in_locus = self

                            total_membership_list.append(newprot)

                            organism.proteins.append(newprot)


            del(seq_record)

        except ValueError,e:
            print str(e), organism.name

        except AssertionError,e:
            print str(e), organism.name

        except UnboundLocalError,e:
            print str(e), organism.name

        handle.close()

        total_membership_list = list(set(total_membership_list))
        total_membership_list.sort(key=lambda x: x.start_bp)
        return total_membership_list


    def write_out_locus_fasta(self):

        fasta=[]
        for prot in self.locus_total_membership:
            fasta.append('>' + prot.accession +
                             "," + prot.hit_name_best +
                             "," + prot.product + 
                             '\n' +prot.translation + '\n')

        faastring = "".join(fasta)

        if not os.path.exists('./locus_fastas/'):
            os.makedirs('./locus_fastas/')

        filename = ('./locus_fastas/' + 
                    self.locus_parent_organism.accession + 
                    str(self.locus_min_hit_boundary) + '.fasta')

        write_fasta = open(filename, 'w')
        write_fasta.write(faastring)
        write_fasta.close()

class LocusView:

    def __init__(self, Locus, hit_detail_table=False, xlims=None):

        self.generate_locus_view(Locus, xlims)

        if hit_detail_table==True:
            self.show_locus_hit_details(Locus)

    def generate_locus_dataframe(self, Locus):
        
        data_tuple_list = []

        print '\n'
        print '-'*70, '\n','-'*70
        print "Organism: ", Locus.locus_parent_organism.name
        print 'Locus id:', id(Locus)



        for protein in Locus.locus_total_membership:
            if len(protein.hmm_hit_list) > 0:

                #print protein.hmm_hit_list[0].__dict__

                protein_hit_query = protein.hit_name_best
                protein_hit_evalue = protein.hit_evalue_best
                protein_hit_bitscore = protein.hit_bitscore_best
                protein_hit_bias = protein.hit_bias_best
                #protein_hsps = protein.hmm_hit_list[0]._items

            else:
                protein_hit_query = '-'
                protein_hit_evalue = '-'
                protein_hit_bitscore = '-'
                protein_hit_bias = '-'

            data_tuple_list.append((protein.accession, protein.product[:22], 
                protein_hit_query,protein_hit_evalue,protein_hit_bitscore,
                protein_hit_bias))

        cols = ['accession', 'name', 'query', 'evalue', 'bitscore', 'bias']

        df = DataFrame(data_tuple_list, columns=cols)

        return df[['accession', 'query', 'evalue', 'bitscore', 'bias', 'name']]



    def generate_locus_view(self, Locus, xlims):

        #set_option('expand_frame_repr', False)
        #figsize(20,5)

        df = self.generate_locus_dataframe(Locus)

        if xlims !=  None:
            xmin_value = xlims[0]
            xmax_value = xlims[1]
        else:
            xmin_value = Locus.locus_min_hit_boundary - Locus.locus_min_hit_boundary
            xmax_value = Locus.locus_max_hit_boundary - Locus.locus_min_hit_boundary

        ax = plt.axes()
        #plt.figure(num=None, figsize=(20,5))

        for n, protein in enumerate(Locus.locus_total_membership):

            colordict = Locus.locus_parent_organism.parent_db.search.protein_arrow_color_dict

            if protein.strand == 1:
                arrow_start = protein.start_bp - Locus.locus_min_hit_boundary
                arrow_end = protein.end_bp - protein.start_bp
            else:
                arrow_start = protein.end_bp - Locus.locus_min_hit_boundary
                arrow_end = protein.start_bp - protein.end_bp

            if len(protein.hmm_hit_list) != 0:
                protname = protein.hit_name_best
                arrow_color =  colordict[protname]
            else:
                arrow_color = '#EEE7EB'

            ax.arrow(arrow_start, 100, arrow_end, 0, head_width=30, width=20,
                color=arrow_color, head_length=200, length_includes_head=True,
                 fill=True, ec="black", lw=1)



            if len(protein.hmm_hit_list) > 0:
                hitdf = protein.hit_dataframe.reset_index()
                ystart = 80 if (n % 2 == 0) else 120

                for i in range(0, len(hitdf)):

                    if protein.strand == 1:
                        line_start = protein.start_bp - Locus.locus_min_hit_boundary + hitdf.ix[i].hsp_start*3
                        line_end = protein.end_bp - Locus.locus_min_hit_boundary - (protein.numb_residues - hitdf.ix[i].hsp_end)*3
                    else:
                        line_start = protein.start_bp - Locus.locus_min_hit_boundary + (protein.numb_residues - hitdf.ix[i].hsp_end)*3
                        line_end = protein.end_bp - Locus.locus_min_hit_boundary - hitdf.ix[i].hsp_start*3

                    plt.plot([line_start, line_end], [ystart, ystart], 'k-', lw=2)

                    xtextpos = line_start

                    if (n % 2 == 0):
                        ytextpos = ystart - 8
                    else: 
                        ytextpos = ystart+2

                    label = str(i) + " " + hitdf.ix[i]['name']# + " " + str(hitdf.ix[i]['evalue'])[:3]
                    plt.annotate(label, xy=(xtextpos, ytextpos))

                    if (n % 2 == 0):
                        ystart -= 10
                    else:
                        ystart +=10


        plt.axis('on')
        pylab.ylim([0,200])
        pylab.xlim([xmin_value, xmax_value])
        #savefig('image.svg', dpi=300, format='pdf')
        plt.show() 

        print df


    def show_locus_hit_details(self, Locus):
        for hit in Locus.locus_hit_membership:
            try:
                print hit.hit_dataframe.sort(columns='bitscore', ascending=False)
            except AttributeError,e:
                print str(e), 'attribute error for ', hit

class FinalDataFrame:

    '''
    Package all data into pandas.DataFrame
    '''

    def __init__(self,OrganismDB):

        self.df = self.make_df(OrganismDB)


    def make_df(self, OrganismDB):

        list_of_hit_dicts = []

        for i in range(0, len(OrganismDB.organisms)):
            organism = OrganismDB.organisms[i]

            for j in range(0, len(organism.proteins)):
                protein = organism.proteins[j]
                
                if len(protein.hmm_hit_list) != 0:
                    
                    hit_dict = OrderedDict()
                    
                    hit_dict['org_name'] = organism.name
                    hit_dict['org_acc'] = organism.accession
                    hit_dict['org_phylum'] = organism.phylum
                    hit_dict['org_class'] = organism.clazz
                    hit_dict['org_order'] = organism.order
                    hit_dict['org_family'] = organism.family
                    hit_dict['org_genus'] = organism.genus
                    hit_dict['org_species'] = organism.species
                    hit_dict['org_tree_order'] = organism.tree_order
                    hit_dict['org_genome_length'] = organism.genome_length
                    hit_dict['org_prot_count'] = len(organism.proteins)
                    hit_dict['org_numb_loci'] = len(organism.loci)
                    hit_dict['prot_acc'] = protein.accession
                    hit_dict['prot_gi'] = protein.gi
                    hit_dict['prot_product'] = protein.product
                    hit_dict['prot_translation'] = protein.translation
                    hit_dict['prot_numb_of_res'] = protein.numb_residues
                    hit_dict['hit_query'] = protein.hit_name_best
                    hit_dict['hit_evalue'] = protein.hit_evalue_best
                    hit_dict['hit_bitscore'] = protein.hit_bitscore_best
                    hit_dict['hit_bias'] = protein.hit_bias_best
                    hit_dict['locus_id'] = protein.is_in_locus
                    
                    list_of_hit_dicts.append(hit_dict)
                
        
        df = DataFrame(list_of_hit_dicts)
        
        print df.index

        cols = ['org_name',
                'org_acc',
                'org_phylum',
                'org_class',
                'org_order',
                'org_family',
                'org_genus',
                'org_species',
                'org_tree_order',
                'org_genome_length',
                'org_prot_count',
                'org_numb_loci',
                'prot_acc',
                'prot_gi',
                'prot_product',
                'prot_translation',
                'prot_numb_of_res',
                'hit_query',
                'hit_evalue',
                'hit_bitscore',
                'hit_bias',
                'locus_id']
        
        df = df[cols]
        
        return df

class HeatMap:

    def __init__(self, DataFrame, by_locus=False, cols=None, subset=None, singleletters=None):

        self.unstacked_df = self.unstack_df(DataFrame, by_locus, cols, subset)

        self.heatmap = self.make_heatmap(self.unstacked_df, singleletters)

    def unstack_df(self, DataFrame, by_locus, cols, subset):

        if by_locus == True:
            colheads = ['org_species', 'locus_id', 'org_tree_order', 'hit_query']
        else:
            colheads = ['org_species', 'org_tree_order', 'hit_query']


        unstacked_df = DataFrame.groupby(colheads).size().unstack()

        if subset != None:
            unstacked_df = unstacked_df.dropna(subset=subset)

        unstacked_df = unstacked_df.fillna(0).sortlevel('org_tree_order', ascending=False)


        if cols != None:
            unstacked_df=unstacked_df[cols]

        return unstacked_df


    def make_heatmap(self, unstacked_df, singleletters):

        fig, ax = plt.subplots(num=None, figsize=(10,len(unstacked_df)/3), dpi=80, facecolor='w', edgecolor='k')


        #heatmap = ax.pcolor(unstacked_df, cmap=plt.cm.Reds, alpha=2, vmax = 5)
        #heatmap = ax.pcolor(unstacked_df, cmap=plt.cm.gist_ncar_r, alpha=20, vmax = 20)
        #heatmap = ax.pcolor(unstacked_df, cmap=plt.cm.YlGnBu, alpha=20, vmax = 2)
        heatmap = ax.pcolor(unstacked_df, cmap=plt.cm.jet, alpha=10, vmax = 5)

       # ax.set_title('140616 - Esp distribution in actinobacteria')

        #cb = plt.colorbar(heatmap)
        #cb.set_label('# of copies')

        species_names_only = ['%s locus:%s' % (x[0],str(x[1])[-12:]) for x in unstacked_df.index.values]

        ax.set_aspect('equal')
        ax.yaxis.set_ticks(range(0, len(unstacked_df.values)))
        ax.xaxis.set_ticks(range(0, len(unstacked_df.columns)))
        ax.set_xticklabels(unstacked_df.columns, rotation='90')
        ax.set_yticklabels(species_names_only)
        #ax.set_yticklabels(unstacked_df.index.values)
        ax.tick_params(axis='both', left='off', right='off', bottom='off', top='off')
        #ax.set_xticks(np.range(data.shape[0])+0.5, minor=False)
        #ax.set_yticks(np.range(data.shape[1])+0.5, minor=False)
        #ax.invert_yaxis()
        #ax.xaxis.tick_top()

        plt.grid(True, color='black', ls='-', linewidth=0.5)

        '''exerimental: displaying text on the heatmap'''

        if singleletters != None:

            for y in range(unstacked_df.values.shape[0]):
                for x in range(unstacked_df.values.shape[1]):
                    plt.text(x + 0.5, y + 0.5, '%.4s' % singleletters[(x)],
                             horizontalalignment='center',
                             verticalalignment='center',
                             )  
        plt.savefig("out.svg")
        plt.show()

        #print species_names_only

    def make_heatmap_text(self, unstacked_df):

        fig, ax = plt.subplots(num=None, figsize=(10,len(unstacked_df)/3), dpi=80, facecolor='w', edgecolor='k')


        #heatmap = ax.pcolor(unstacked_df, cmap=plt.cm.Reds, alpha=2, vmax = 5)
        #heatmap = ax.pcolor(unstacked_df, cmap=plt.cm.gist_ncar_r, alpha=20, vmax = 20)
        #heatmap = ax.pcolor(unstacked_df, cmap=plt.cm.YlGnBu, alpha=20, vmax = 2)
        heatmap = ax.pcolor(unstacked_df, cmap=plt.cm.jet, alpha=10, vmax = 5)

       # ax.set_title('140616 - Esp distribution in actinobacteria')

        #cb = plt.colorbar(heatmap)
        #cb.set_label('# of copies')

        species_names_only = ['%s locus:%s' % (x[0],str(x[1])[-12:]) for x in unstacked_df.index.values]

        ax.set_aspect('equal')
        ax.yaxis.set_ticks(range(0, len(unstacked_df.values)))
        ax.xaxis.set_ticks(range(0, len(unstacked_df.columns)))
        ax.set_xticklabels(unstacked_df.columns, rotation='90')
        ax.set_yticklabels(species_names_only)
        #ax.set_yticklabels(unstacked_df.index.values)
        ax.tick_params(axis='both', left='off', right='off', bottom='off', top='off')
        #ax.set_xticks(np.range(data.shape[0])+0.5, minor=False)
        #ax.set_yticks(np.range(data.shape[1])+0.5, minor=False)
        #ax.invert_yaxis()
        #ax.xaxis.tick_top()
        plt.grid(True, color='black', ls='-', linewidth=0.5)

        '''exerimental: displaying text on the heatmap'''

        for y in range(unstacked_df.values.shape[0]):
            for x in range(unstacked_df.values.shape[1]):
                plt.text(x + 0.5, y + 0.5, '%.4s' % 'A',
                         horizontalalignment='center',
                         verticalalignment='center',
                         )  

        plt.show()

        #print species_names_only

class RelatedProteinGroup:

    '''
    An object representing a group of related proteins
    to be used for generating alignments, phylogeny, etc.
    
    Input is a list of Protein objects, e.g. of the same type that were
    identified in the Hmm search & where found in a cluster.

    Can output a fasta file for each group for making alignments & trees
    '''

    def __init__(self, input_df):

       self.make_related_protein_fasta_from_dataframe(input_df)


    def make_related_protein_fasta_from_dataframe(self, input_df):

        '''
        DataFrame should have 
        '''

        dirname = './group_fastas'

        if not os.path.exists(dirname):
            os.makedirs(dirname)

        unique_hit_queries = set(input_df.hit_query)

        for hq in unique_hit_queries:

            fasta = []

            subdf = input_df[input_df.hit_query==hq].reset_index()

            for i in range(0, len(subdf)):

                fasta.append('>' + subdf.ix[i].org_name.replace(" ", "-") +
                             "," + subdf.ix[i].hit_query +
                             "," + subdf.ix[i].prot_acc + 
                             '\n' + subdf.ix[i].prot_translation + '\n')

            faastring = "".join(fasta)

            filename = './group_fastas/' + hq + '.fasta'
            write_fasta = open(filename, 'w')
            write_fasta.write(faastring)
            write_fasta.close()

'''
def make_16S(OrganismDB):

        for org in OrganismDB.genome_list:


        hmmbuild_output = subprocess.call(["hmmbuild", './16S_rRNA/16S_rRNA.hmm',
            './16S_rRNA/16S_rRNA_alignment.fasta'])

        hmmsearch_output = subprocess.check_output(["hmmsearch",
         "--cpu", str(processors), './16S_rRNA/16S_rRNA.hmm',
          'combined_fasta'])

        f = open('./16S_rRNA/16S_rRNA_result.out', 'w')
        f.write(hmmsearch_output)
        f.close ()
'''