# -*- coding: utf-8 -*-
"""
The MIT License (MIT)

Copyright 2015 Umbrella Tech.

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
__author__ = 'Kelson da Costa Medeiros <kelsoncm@gmail.com>'

import unittest
from datetime import date
import pyaboleto
import pyaboleto.itau
import pyaboleto.bb


DATA_TESTE = date(2007, 12, 31)


class BaseTestCase(unittest.TestCase):
    def _test_padrao(self):
        end = pyaboleto.Endereco('12345-123', 'Logradouro', 'Nº', 'Complemento', 'Bairro', 'Cidade', 'UF', 'Brasil')
        sac = pyaboleto.Sacado('Nome do cidadão', '123.456.789-01', end, '123465 SSP/UF')
        ced = pyaboleto.Cedente('Nome da empresa', '12.345.678/9012-34', end)
        return end, sac, ced


class RootTestCase(BaseTestCase):

    def test_modulo11(self):
        self.assertEqual('x', pyaboleto.modulo11('6', 'x'))
        self.assertEqual('x', pyaboleto.modulo11('0', 'z', 'x'))
        self.assertEqual('0-x', pyaboleto.modulo11('0', 'z', 'x', True))
        self.assertEqual('0=x', pyaboleto.modulo11('0', 'z', 'x', True, separador='='))

    def test_fator_vencimento(self):
        con = pyaboleto.Convenio('7777777', '22', pyaboleto.Banco('333', 'FEBRABAN'), '5555-5', '66666-6')
        bol = pyaboleto.Boleto('07006700', DATA_TESTE, 34.75, con, None, None)
        self.assertEqual('3737', bol.fator_vencimento)

    def test_caminho_feliz(self):
        end, sac, ced = self._test_padrao()
        con = pyaboleto.Convenio('123456', '21', pyaboleto.Banco('000', 'FEBRABAN'), '1234-5', '12345-6')
        bol = pyaboleto.Boleto('123456789', DATA_TESTE, 123.45, con, ced, sac)

        bol._validar_codigo_barras()
        self.assertEqual(True, True)

    def test_banco_errado(self):
        con = pyaboleto.Convenio('', '', pyaboleto.Banco('00', 'FEBRABAN'), '1234-5', '12345-6')
        bol = pyaboleto.Boleto('07006700', DATA_TESTE, 34.75, con, None, None)
        with self.assertRaisesRegexp(pyaboleto.PYABoletoExcpetion, 'O banco deve conter.*'):
            bol._validar_codigo_barras()

    def test_moeda_errado(self):
        con = pyaboleto.Convenio('', '', pyaboleto.Banco('000', 'FEBRABAN'), '1234-5', '12345-6')
        bol = pyaboleto.Boleto('07006700', DATA_TESTE, 34.75, con, None, None)
        bol.moeda = '99'
        with self.assertRaisesRegexp(pyaboleto.PYABoletoExcpetion, 'A moeda deve conter.*'):
            bol._validar_codigo_barras()

    def test_valor_total_errado(self):
        con = pyaboleto.Convenio('', '', pyaboleto.Banco('000', 'FEBRABAN'), '1234-5', '12345-6')
        bol = pyaboleto.Boleto('07006700', DATA_TESTE, 123456798.75, con, None, None)
        with self.assertRaisesRegexp(pyaboleto.PYABoletoExcpetion, 'O valor total deve ser.*'):
            bol._validar_codigo_barras()

    def test_strs(self):
        end_str = 'Logradouro Nº, Complemento, Bairro, Cidade-UF, Brasil, CEP: 12345-123'
        end_str2 = 'Logradouro Nº, Bairro, Cidade-UF, Brasil, CEP: 12345-123'
        sac_str = 'Nome do cidadão - 123.456.789-01 - 123465 SSP/UF - %s' % end_str
        ced_str = 'Nome da empresa - 12.345.678/9012-34 - %s' % end_str
        con_str = '7777777 - 22, 333 - 5555-5 - 66666-6'
        bol_str = '33390.00006 00000.000000 00000.000000 4 37370000003475'

        end, sac, ced = self._test_padrao()
        self.assertEqual(end_str, str(end))
        self.assertEqual(sac_str, str(sac))
        self.assertEqual(ced_str, str(ced))
        end.complemento = None
        self.assertEqual(end_str2, str(end))

        con = pyaboleto.Convenio('7777777', '22', pyaboleto.Banco('333', 'FEBRABAN'), '5555-5', '66666-6')
        self.assertEqual(con_str, str(con))

        bol = pyaboleto.Boleto('07006700', DATA_TESTE, 34.75, con, None, None)
        self.assertEqual(bol_str, str(bol))

    def test_implementacao_errada(self):
        class FailBoleto(pyaboleto.Boleto):
            @property
            def campo_livre(self):
                return str.zfill('0', 24)
        con = pyaboleto.Convenio('7777777', '22', pyaboleto.Banco('333', 'FEBRABAN'), '5555-5', '66666-6')
        bol = FailBoleto('07006700', DATA_TESTE, 34.75, con, None, None)
        with self.assertRaisesRegexp(pyaboleto.PYABoletoExcpetion, 'O campo livre deve conter 25 digito.*'):
            self.assertEqual(bol.codigo_barras, '33391648100000034750000000000000000000000000')

class ItauTestCase(BaseTestCase):
    def test_caminho_feliz(self):
        con = pyaboleto.Convenio(None, '109', pyaboleto.itau.banco_itau, '9314-9', '32857-7')
        bol = pyaboleto.itau.ItauBoleto('07006700', DATA_TESTE, 34.75, con, None, None)

        self.assertEqual('1090700670069314328577000', bol.campo_livre)
        self.assertEqual('34193373700000034751090700670069314328577000', bol.codigo_barras)
        self.assertEqual('34191.09073 00670.069319 43285.770004 3 37370000003475', bol.linha_digitavel)

    def test_carteira_errada(self):
        con = pyaboleto.Convenio('123456', '21', pyaboleto.itau.banco_itau, '1234-5', '12345-6')
        bol = pyaboleto.itau.ItauBoleto('07006700', DATA_TESTE, 34.75, con, None, None)
        with self.assertRaisesRegexp(pyaboleto.PYABoletoExcpetion, '.*carteira deve conter.*'):
            bol._validar_codigo_barras()

    def test_agencia_errada(self):
        con = pyaboleto.Convenio('123456', '109', pyaboleto.itau.banco_itau, '1234', '12345')
        bol = pyaboleto.itau.ItauBoleto('07006700', DATA_TESTE, 34.75, con, None, None)
        with self.assertRaisesRegexp(pyaboleto.PYABoletoExcpetion, '.*agência deve conter.*'):
            bol._validar_codigo_barras()

    def test_conta_errada(self):
        con = pyaboleto.Convenio('123456', '109', pyaboleto.itau.banco_itau, '1234-5', '12345')
        bol = pyaboleto.itau.ItauBoleto('07006700', DATA_TESTE, 34.75, con, None, None)
        with self.assertRaisesRegexp(pyaboleto.PYABoletoExcpetion, '.*conta deve conter.*'):
            bol._validar_codigo_barras()


class BBTestCase(BaseTestCase):
    def test_caminho_feliz_convenio4(self):
        con = pyaboleto.Convenio('5094', '31', pyaboleto.bb.banco_brasil, '1606-0', '06809350-0')
        bol = pyaboleto.bb.BBBoleto('1234567-0', DATA_TESTE, 1.0, con, None, None)

        self.assertEqual('5094123456716060680935031', bol.campo_livre)
        self.assertEqual('00197373700000001005094123456716060680935031', bol.codigo_barras)
        self.assertEqual('00195.09413 23456.716069 06809.350314 7 37370000000100', bol.linha_digitavel)

    def test_caminho_feliz_convenio6(self):
        con = pyaboleto.Convenio('050094', '31', pyaboleto.bb.banco_brasil, '1606-0', '06809350-0')
        bol = pyaboleto.bb.BBBoleto('01448-0', DATA_TESTE, 1.0, con, None, None)

        self.assertEqual('0500940144816060680935031', bol.campo_livre)
        self.assertEqual('00193373700000001000500940144816060680935031', bol.codigo_barras)
        self.assertEqual('00190.50095 40144.816069 06809.350314 3 37370000000100', bol.linha_digitavel)

    def test_caminho_feliz_convenio6_carteira21(self):
        con = pyaboleto.Convenio('050094', '21', pyaboleto.bb.banco_brasil, '1606-0', '06809350-0')
        bol = pyaboleto.bb.BBBoleto('12345678901234567', DATA_TESTE, 1.0, con, None, None)

        self.assertEqual('0500941234567890123456721', bol.campo_livre)
        self.assertEqual('00196373700000001000500941234567890123456721', bol.codigo_barras)
        self.assertEqual('00190.50095 41234.567893 01234.567210 6 37370000000100', bol.linha_digitavel)

    def test_caminho_feliz_convenio7(self):
        con = pyaboleto.Convenio('1050094', '31', pyaboleto.bb.banco_brasil, '1606-0', '06809350-0')
        bol = pyaboleto.bb.BBBoleto('1234657890-0', DATA_TESTE, 1.0, con, None, None)

        self.assertEqual('0000001050094123465789031', bol.campo_livre)
        self.assertEqual('00192373700000001000000001050094123465789031', bol.codigo_barras)
        self.assertEqual('00190.00009 01050.094125 34657.890314 2 37370000000100', bol.linha_digitavel)
