# -*- coding: utf-8 -*-
"""
The MIT License (MIT)

Copyright 2013 Umbrella Tech.

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


from . import *


class BBBoleto(Boleto):
    """
    Gera o campo livre do código de barras.
    """

    def gerar_campo_livre(self, dados):
        dados['campo_livre'] = str.zfill(self.numero + dados['nosso_numero'], 25)
        if len(dados['convenio_numero']) == 4:
            pass
        elif len(dados['convenio_numero']) == 6:
            if dados['carteira'] != '21':
                dados['campo_livre'] = str.zfill(self.numero + dados['nosso_numero'] + modulo11(dados['nosso_numero'], 0, 0), 25)
            else:
                pass
        elif len(dados['convenio_numero']) == 7:
            pass
        else:
            super(BBConvenio, self).gerar_campo_livre(dados)
        return dados


def show_me():
    bol = teste_me()
    old = bol.convenio
    bol.convenio = BBBoleto(old.banco, old.carteira, old.numero)
    bol.gerar_codigo_barras()
    bol.gerar_linha_digitavel()
    print(bol)