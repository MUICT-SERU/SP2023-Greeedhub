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

DATA_TESTE = date(2015, 7, 6)

class BaseTestCase(unittest.TestCase):
    def _test_padrao(self):
        end = pyaboleto.Endereco('12345-123', 'Logradouro', 'Nº', 'Complemento', 'Bairro', 'Cidade', 'UF', 'Brasil')
        sac = pyaboleto.Sacado('Nome do cidadão', '123.456.789-01', end, '123465 SSP/UF')
        ced = pyaboleto.Cedente('Nome da empresa', '12.345.678/9012-34', end)
        return end, sac, ced


class RootTestCase(BaseTestCase):

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
        bol_str = '33390.00006 00000.000000 00000.000000 1 64810000003475'

        end, sac, ced = self._test_padrao()
        self.assertEqual(str(end), end_str)
        self.assertEqual(str(sac), sac_str)
        self.assertEqual(str(ced), ced_str)
        end.complemento = None
        self.assertEqual(str(end), end_str2)

        con = pyaboleto.Convenio('7777777', '22', pyaboleto.Banco('333', 'FEBRABAN'), '5555-5', '66666-6')
        self.assertEqual(str(con), con_str)

        bol = pyaboleto.Boleto('07006700', DATA_TESTE, 34.75, con, None, None)
        self.assertEqual(str(bol), bol_str)

    def test_implementacao_errada(self):
        class FailBoleto(pyaboleto.Boleto):
            def campo_livre(self):
                return str.zfill('0', 24)
        con = pyaboleto.Convenio('7777777', '22', pyaboleto.Banco('333', 'FEBRABAN'), '5555-5', '66666-6')
        bol = FailBoleto('07006700', DATA_TESTE, 34.75, con, None, None)
        with self.assertRaisesRegexp(pyaboleto.PYABoletoExcpetion, 'O campo livre deve conter 25 digito.*'):
            tmp = bol.codigo_barras

    def test_modulo11(self):
        self.assertEqual(pyaboleto.modulo11('6', 'x'), 'x')
        self.assertEqual(pyaboleto.modulo11('0', 'z', 'x'), 'x')
        self.assertEqual(pyaboleto.modulo11('0', 'z', 'x', True), '0-x')
        self.assertEqual(pyaboleto.modulo11('0', 'z', 'x', True, separador='='), '0=x')

class ItauTestCase(BaseTestCase):
    def test_caminho_feliz(self):
        con = pyaboleto.Convenio(None, '109', pyaboleto.itau.banco_itau, '9314-9', '32857-7')
        bol = pyaboleto.itau.ItauBoleto('07006700', DATA_TESTE, 34.75, con, None, None)

        self.assertEqual(bol.campo_livre, '1090700670069314328577000')
        self.assertEqual(bol.codigo_barras, '34191648100000034751090700670069314328577000')
        self.assertEqual(bol.linha_digitavel, '34191.09073 00670.069319 43285.770004 1 64810000003475')

    def test_carteira_errada(self):
        from pyaboleto.itau import ItauBoleto, banco_itau
        con = pyaboleto.Convenio('123456', '21', pyaboleto.itau.banco_itau, '1234-5', '12345-6')
        bol = pyaboleto.itau.ItauBoleto('07006700', DATA_TESTE, 34.75, con, None, None)
        with self.assertRaisesRegexp(pyaboleto.PYABoletoExcpetion, 'A carteira deve conter.*'):
            bol._validar_codigo_barras()

    def test_agencia_errada(self):
        con = pyaboleto.Convenio('123456', '109', pyaboleto.itau.banco_itau, '1234', '12345')
        bol = pyaboleto.itau.ItauBoleto('07006700', DATA_TESTE, 34.75, con, None, None)
        with self.assertRaisesRegexp(pyaboleto.PYABoletoExcpetion, 'A agência deve conter.*'):
            bol._validar_codigo_barras()

    def test_conta_errada(self):
        con = pyaboleto.Convenio('123456', '109', pyaboleto.itau.banco_itau, '1234-5', '12345')
        bol = pyaboleto.itau.ItauBoleto('07006700', DATA_TESTE, 34.75, con, None, None)
        with self.assertRaisesRegexp(pyaboleto.PYABoletoExcpetion, 'A conta deve conter.*'):
            bol._validar_codigo_barras()
