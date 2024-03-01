# -*- coding: utf-8 -*-
# © 2016 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import os
import suds
from pytrustnfe.xml import render_xml, sanitize_response
from pytrustnfe.client import get_authenticated_client
from pytrustnfe.certificado import extract_cert_and_key_from_pfx, save_cert_key
from pytrustnfe.nfse.assinatura import Assinatura


def _send(certificado, method, **kwargs):
    path = os.path.join(os.path.dirname(__file__), 'templates')
    xml_send = render_xml(path, '%s.xml' % method, False, **kwargs)

    base_url = ''
    if kwargs['ambiente'] == 'producao':
        base_url = 'https://producao.ginfes.com.br/ServiceGinfesImpl?wsdl'
    else:
        base_url = 'https://homologacao.ginfes.com.br/ServiceGinfesImpl?wsdl'

    cert, key = extract_cert_and_key_from_pfx(
        certificado.pfx, certificado.password)
    cert, key = save_cert_key(cert, key)

    client = get_authenticated_client(base_url, cert, key)

    pfx_path = certificado.save_pfx()
    signer = Assinatura(pfx_path, certificado.password)
    xml_send = signer.assina_xml(xml_send, '')

    try:
        header = '<ns2:cabecalho xmlns:ns2="http://www.ginfes.com.br/cabecalho_v03.xsd" versao="3"><versaoDados>3</versaoDados></ns2:cabecalho>' #noqa
        response = getattr(client.service, method)(header, xml_send)
    except suds.WebFault, e:
        return {
            'sent_xml': xml_send,
            'received_xml': e.fault.faultstring,
            'object': None
        }

    response, obj = sanitize_response(response)
    return {
        'sent_xml': xml_send,
        'received_xml': response,
        'object': obj
    }


def envio_lote_rps(certificado, **kwargs):
    return _send(certificado, 'RecepcionarLoteRpsV3', **kwargs)


def consultar_situacao_lote(certificado, **kwargs):
    return _send(certificado, 'ConsultarSituacaoLoteRpsV3', **kwargs)


def consultar_nfse_por_rps(certificado, **kwargs):
    return _send(certificado, 'ConsultarNfsePorRpsV3', **kwargs)


def consultar_lote(certificado, **kwargs):
    return _send(certificado, 'ConsultarLoteRpsV3', **kwargs)


def consultar_nfse(certificado, **kwargs):
    return _send(certificado, 'ConsultarNfseV3', **kwargs)


def cancelar_nfse(certificado, **kwargs):
    return _send(certificado, 'CancelarNfseV3', **kwargs)
