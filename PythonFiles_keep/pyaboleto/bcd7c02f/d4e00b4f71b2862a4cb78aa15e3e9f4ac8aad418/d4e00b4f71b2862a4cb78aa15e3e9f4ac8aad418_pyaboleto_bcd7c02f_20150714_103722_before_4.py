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
from pyaboleto import Endereco, Sacado, Cedente, Convenio, PYABoletoExcpetion

DATA_TESTE = date(2015, 7, 6)

class BaseTestCase(unittest.TestCase):
    def _test_padrao(self):
        end = Endereco('12345-123', 'Logradouro', 'Nº', 'Complemento', 'Bairro', 'Cidade', 'UF', 'Brasil')
        sac = Sacado('Nome do cidadão', '123.456.789-01', end, '123465 SSP/UF')
        ced = Cedente('Nome da empresa', '12.345.678/9012-34', end)
        return end, sac, ced


class RootTestCase(BaseTestCase):

    def test_caminho_feliz(self):
        from pyaboleto import Boleto, Banco
        end, sac, ced = self._test_padrao()
        con = Convenio('123456', '21', Banco('000', 'FEBRABAN'), '1234-5', '12345-6')
        bol = Boleto('123456789', DATA_TESTE, 123.45, con, ced, sac)

        bol._validar_codigo_barras()
        self.assertEqual(True, True)

    def test_banco_errado(self):
        from pyaboleto import Boleto, Banco
        end, sac, ced = self._test_padrao()
        con = Convenio('123456', '21', Banco('00', 'FEBRABAN'), '1234-5', '12345-6')
        bol = Boleto('07006700', DATA_TESTE, 34.75, con, ced, sac)

        with self.assertRaises(Exception) as context:
            bol._validar_codigo_barras()

class ItauTestCase(BaseTestCase):
    def test_caminho_feliz(self):
        from pyaboleto.itau import ItauBoleto, banco_itau
        end, sac, ced = self._test_padrao()
        con = Convenio(None, '109', banco_itau, '9314-9', '32857-7')
        bol = ItauBoleto('07006700', DATA_TESTE, 34.75, con, ced, sac)

        self.assertEqual(bol.campo_livre, '1090700670069314328577000')
        self.assertEqual(bol.codigo_barras, '34191648100000034751090700670069314328577000')
        self.assertEqual(bol.linha_digitavel, '34191.09073 00670.069319 43285.770004 1 64810000003475')

    def test_carteira_errada(self):
        from pyaboleto.itau import ItauBoleto, banco_itau
        con = Convenio('123456', '21', banco_itau, '1234-5', '12345-6')
        bol = ItauBoleto('07006700', DATA_TESTE, 34.75, con, None, None)

        with self.assertRaisesRegexp(PYABoletoExcpetion, 'A carteira deve conter.*'):
            bol._validar_codigo_barras()

    def test_agencia_errada(self):
        from pyaboleto.itau import ItauBoleto, banco_itau
        end, sac, ced = self._test_padrao()
        con = Convenio('123456', '109', banco_itau, '1234', '12345')
        bol = ItauBoleto('07006700', DATA_TESTE, 34.75, con, ced, sac)

        with self.assertRaisesRegexp(PYABoletoExcpetion, 'A agência deve conter.*'):
            bol._validar_codigo_barras()

    def test_conta_errada(self):
        from pyaboleto.itau import ItauBoleto, banco_itau
        end, sac, ced = self._test_padrao()
        con = Convenio('123456', '109', banco_itau, '1234-5', '12345')
        bol = ItauBoleto('07006700', DATA_TESTE, 34.75, con, None, None)

        with self.assertRaisesRegexp(PYABoletoExcpetion, 'A conta deve conter.*'):
            bol._validar_codigo_barras()
