#coding=utf-8
'''
Created on Jun 14, 2015

@author: danimar
'''

from lxml import objectify
from uuid import uuid4
from pytrustnfe.HttpClient import HttpClient
from pytrustnfe.Certificado import converte_pfx_pem

import logging
logging.basicConfig(level=logging.INFO)
logging.getLogger('suds.client').setLevel(logging.DEBUG)
logging.getLogger('suds.transport').setLevel(logging.DEBUG)

from pytrustnfe.Strings import CONSULTA_CADASTRO_COMPLETA

class Comunicacao(object):
        
    def __init__(self, certificado, senha):
        self.certificado = certificado
        self.senha = senha
        
        
    def _preparar_temp_pem(self):
        chave_temp = '/tmp/' + uuid4().hex
        certificado_temp = '/tmp/' + uuid4().hex
        
        chave, certificado = converte_pfx_pem(self.certificado, self.senha)
        arq_temp = open(chave_temp, 'w')
        arq_temp.write(chave)
        arq_temp.close()
        
        arq_temp = open(certificado_temp, 'w')
        arq_temp.write(certificado)
        arq_temp.close()
        
        return chave_temp, certificado_temp
        
    def consulta_cadastro(self, obj_consulta):
        chave, certificado = self._preparar_temp_pem()
        
        client = HttpClient('nfe.fazenda.sp.gov.br', chave, certificado)
        xml_retorno = client.post_xml('/ws/cadconsultacadastro2.asmx', CONSULTA_CADASTRO_COMPLETA)
        
        obj = objectify.fromstring(xml_retorno)
        return xml_retorno, obj
    
    def envio_nfe(self):
        chave, certificado = self._preparar_temp_pem()
        
        c = HttpClient('cad.sefazrs.rs.gov.br', chave, certificado)
        
        xml_retorno =  c.post_xml('/ws/cadconsultacadastro/cadconsultacadastro2.asmx', '')                
        obj = objectify.fromstring(xml_retorno)

        return xml_retorno, obj
        
        
        