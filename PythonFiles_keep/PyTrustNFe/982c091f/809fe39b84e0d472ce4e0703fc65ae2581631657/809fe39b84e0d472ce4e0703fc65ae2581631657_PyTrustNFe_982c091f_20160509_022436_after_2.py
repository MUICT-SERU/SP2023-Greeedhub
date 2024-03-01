# coding=utf-8
'''
Created on Jun 14, 2015

@author: danimar
'''

import suds.client
import suds_requests
import requests
from lxml import objectify
from uuid import uuid4
from pytrustnfe.HttpClient import HttpClient
from pytrustnfe.Certificado import converte_pfx_pem

from xml.dom.minidom import parseString

common_namespaces = {'soap': 'http://www.w3.org/2003/05/soap-envelope'}

soap_body_path = './soap:Envelope/soap:Body'
soap_fault_path = './soap:Envelope/soap:Body/soap:Fault'


class Comunicacao(object):
    url = ''
    web_service = ''
    metodo = ''
    tag_retorno = ''

    def __init__(self, cert, key):
        self.cert = cert
        self.key = key

    def _get_client(self, base_url):
        cache_location = '/tmp/suds'
        cache = suds.cache.DocumentCache(location=cache_location)

        f = open('/tmp/suds/cert_nfe.cer', 'w')
        f.write(self.cert)
        f.close()
        f = open('/tmp/suds/key_nfe.cer', 'w')
        f.write(self.key)
        f.close()
        session = requests.Session()
        session.verify = False
        session.cert = ('/tmp/suds/cert_nfe.cer',
                        '/tmp/suds/key_nfe.cer')

        return suds.client.Client(
            base_url,
            cache=cache,
            transport=suds_requests.RequestsTransport(session)
        )

    def _soap_xml(self, body):
        xml = '''<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope">
<soap:Header>
<nfeCabecMsg xmlns="http://www.portalfiscal.inf.br/nfe/wsdl/'''
        xml += self.metodo
        xml += '''"><cUF>42</cUF><versaoDados>2.00</versaoDados>
</nfeCabecMsg>
</soap:Header>
<soap:Body>
<nfeDadosMsg xmlns="http://www.portalfiscal.inf.br/nfe/wsdl/'''
        xml += self.metodo + '">' + body
        xml += '</nfeDadosMsg></soap:Body></soap:Envelope>'

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

    def _validar_dados(self):
        assert self.url != '', "Url servidor não configurada"
        assert self.web_service != '', "Web service não especificado"
        assert self.certificado != '', "Certificado não configurado"
        assert self.senha != '', "Senha não configurada"
        assert self.metodo != '', "Método não configurado"
        assert self.tag_retorno != '', "Tag de retorno não configurado"

    def _validar_nfe(self, obj):
        if not isinstance(obj, dict):
            raise u"Objeto deve ser um dicionário de valores"

    def _executar_consulta(self, xmlEnviar):
        self._validar_dados()
        # chave, certificado = self._preparar_temp_pem()

        client = HttpClient(self.url, self.certificado, self.senha)
        soap_xml = self._soap_xml(xmlEnviar)
        xml_retorno = client.post_xml(self.web_service, soap_xml)

        dom = parseString(xml_retorno)
        nodes = dom.getElementsByTagNameNS(common_namespaces['soap'], 'Fault')
        if len(nodes) > 0:
            return nodes[0].toxml(), None

        nodes = dom.getElementsByTagName(self.tag_retorno)
        if len(nodes) > 0:
            obj = objectify.fromstring(nodes[0].toxml())
            return nodes[0].toxml(), obj

        return xml_retorno, objectify.fromstring(xml_retorno)
