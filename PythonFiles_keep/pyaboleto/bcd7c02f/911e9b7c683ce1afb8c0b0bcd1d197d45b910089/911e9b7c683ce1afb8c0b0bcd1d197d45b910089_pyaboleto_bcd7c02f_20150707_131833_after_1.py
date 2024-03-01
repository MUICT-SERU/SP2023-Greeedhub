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


from datetime import date


def modulo11(numero, if_dez='0', if_zero='0', mascarado=False, max_fator=9, separador='-'):
    soma = 0
    fator = 2
    for c in reversed(numero):
        soma += int(c) * fator
        fator = 2 if fator >= max_fator else fator + 1;

    resto = (soma * 10) % 11
    if resto == 10:
        resto = if_dez
    elif resto == 0:
        resto = if_zero
    return resto if not mascarado else '%s%s%s' % (numero, separador, resto)


def modulo10(number):
    soma = 0
    fato = 2
    for c in reversed(number):
        soma += int(c) * fato
        fato = 2 if fato == 1 else 1

    resto = soma % 10
    return 10 - resto if resto != 0 else 0


def fator_vencimento(data):
    data_base = date(1997, 10, 7)
    delta = data - data_base
    return delta.days


def put_at(string, at, char):
    lst = list(string)
    lst[at] = char
    return "".join(lst)


def apply_mask():
    pass


class Endereco:

    """
    Classe abstrata que representa uma pessoa, física ou jurídica.
    """

    # end = Endereco('12345-123', 'Av. Imortais', '666', 'Ap. 23', 'Academia', 'Brasileira', 'LT', 'BR')
    # end = Endereco('12345-123', 'Av. Imortais da Academia', '666', 'Academia', 'Brasileira', 'Letras')

    def __init__(self,  cep, logradouro, numero, complemento, bairro, cidade, uf, pais='Brasil'):
        self.cep = cep
        self.logradouro = logradouro
        self.numero = numero
        self.complemento = complemento
        self.bairro = bairro
        self.cidade = cidade
        self.uf = uf
        self.pais = pais

    def __str__(self):
        if self.complemento:
            '''Av. Fernando Pessoa 1234, Ap. 192, Imortais, Academia-AL, Brasil, CEP: 12345-123'''
            return '%s %s, %s, %s, %s-%s, %s, CEP: %s' % \
                   (self.logradouro, self.numero, self.complemento, self.bairro, self.cidade, self.uf, self.pais, self.cep)

        '''Av. Fernando Pessoa 1234, Imortais, Academia-AL, Brasil, CEP: 12345-123'''
        return '%s %s, %s, %s-%s, %s, CEP: %s' % \
               (self.logradouro, self.numero, self.bairro, self.cidade, self.uf, self.pais, self.cep)


class Pessoa:
    """
    Classe abstrata que representa uma pessoa, física ou jurídica.
    """

    def __init__(self, nome, cpf_cnpj, endereco, documento_pessoal=None):
        """
        Inicializa uma nova instância da classe.
        """
        self.nome = nome
        self.cpf_cnpj = cpf_cnpj
        self.endereco = endereco
        self.documento_pessoal = documento_pessoal

    def __str__(self):
        if self.documento_pessoal:
            return '%s - %s - %s - %s' % (self.nome, self.cpf_cnpj, self.documento_pessoal, self.endereco)
        return '%s - %s - %s' % (self.nome, self.cpf_cnpj, self.endereco)


class Sacado(Pessoa):
    # sac = Sacado('Kelson C. Medeiros', '123.456.789-01', end, '123465 SSP/UF')
    # sac = Sacado('Kelson C. Medeiros', '123.456.789-01', end)
    pass


class Cedente(Pessoa):
    # ced = Cedente('Kelson C. Medeiros', '12.345.678/9012-34', end)
    # ced = Cedente('Kelson C. Medeiros', '12.123.123/0001-12', end)
    pass


class Banco:
    """
    Classe abstrata que representa um banco.
    """

        # ban = Banco('001', 'Banco do Brasil', '1234-5', '12.345-6')

    def __init__(self, numero, nome, agencia, conta):
        self.numero = numero
        self.nome = nome
        self.agencia = agencia
        self.conta = conta
        self.codigo = modulo11(self.numero)

    def __str__(self):
        return "%s (%s) %s: %s/%s" % (self.numero, self.codigo, self.nome, self.agencia, self.conta)


class Carteira:

    # car = Carteira(123456789)

    def __init__(self, numero):
        self.numero = numero

    def __str__(self):
        return "%s" % self.numero


class Convenio:
    """
    Classe abstrata que representa o convênio.
    """

    # con = Convenio(ban, car, '123456', '12345678')

    def __init__(self, banco, carteira, numero_convenio, nosso_numero):
        self.banco = banco
        self.carteira = carteira
        self.numero_convenio = numero_convenio
        self.nosso_numero = nosso_numero

    def __str__(self):
        return "%s - %s, %s" % (self.banco, self.carteira, self.numero_convenio)

    def gerar_campo_livre(self):
        raise NotImplementedError()

    @property
    def tamanhos(self):
        raise NotImplementedError()

    @property
    def layout(self):
        raise NotImplementedError()

class Boleto:
    """
    Classe abstrata que representa um boleto.
    """
    def __init__(self, sacado, cedente, convenio, valor_documento, data_vencimento, data_documento, numero_documento):
        self.sacado = sacado
        self.cedente = cedente
        self.convenio = convenio
        self.valor_documento = valor_documento
        self.data_vencimento = data_vencimento
        self.data_documento = data_documento
        self.numero_documento = numero_documento
        self.taxa = None
        self.desconto = None
        self.outra_deducoes = None
        self.multa = None
        self.outros_acrescimos = None
        self.instrucoes = None
        self.demonstrativo = None
        self.quantidade = None
        self.aceite = None
        self.especie = None
        self.local_pagamento = None
        self.codigo_barras = None
        self.linha_digitavel = None
        self.mascara = "00000.00000 00000.000000 00000.000000 0 00000000000000"
        self.erros = []
        self.moeda = 9

    def __str__(self):
        return self.linha_digitavel

    @property
    def total(self):
        return (self.valorDocumento + self.taxa + self.outrosAcrescimos) - (self.desconto + self.outrasDeducoes)
    
    def gerar_codigo_barras(self):
        convenio = self.convenio
        banco = convenio.banco
        total = self.total

        if total < 0:
            raise Exception("Valor total do boleto não pode ser negativo")

        valor = total * 100
        agencia = banco.agencia[0, 4]
        conta = banco.conta[0, 4]

        dados = {
            'banco_numero': banco.numero,
            'moeda': self.moeda,
            'valor': valor,
            'agencia': agencia,
            'convenio_carteira_numero': convenio.carteira.numero,
            'conta': conta,
            'convenio_nosso_numero': convenio.nosso_numero,
            'fator_vencimento': fator_vencimento(self.data_vencimento),
            'numero_convenio': convenio.numero_convenio
        }

        convenio.gerar_campo_livre(dados)

        tamanhos = convenio.tamanhos

        for key, size in tamanhos.items():
            dados[key] = str(dados[key]).zfill(size)[:size]

        # convenio.setNossoNumero(dados['NossoNumero'])

        temp_codigo_barras = convenio.layout.format(dados)

        dv = modulo11(temp_codigo_barras, 1, 1)

        codigo_barras = put_at(temp_codigo_barras, 4, dv)
        return codigo_barras

    def gerar_linha_digitavel(self, codigo_barras):
        """
        Gera a linha digitável baseado em um código de barras.
        """
        # # Campo1 - Posições de 1-4 e 20-24
        # # Campo2 - Posições 25-34
        # # Campo3 - Posições 35-44
        # # Campo4 - Posição 5
        # # Campo5 - Posições 6-19
        # linha_digitavel = codigo_barras[0, 4] + \
        #                  codigo_barras[19, 5] + \
        #                  codigo_barras[24, 10] + \
        #                  codigo_barras[34, 10] + \
        #                  codigo_barras[4, 1] + \
        #                  codigo_barras[5, 14]
        #
        # dv1 = modulo10(linha_digitavel[0, 9])
        # dv2 = modulo10(linha_digitavel[9, 10])
        # dv3 = modulo10(linha_digitavel[19, 10])
        #
        # linha_digitavel = put_at(linha_digitavel, 29, dv3)
        # linha_digitavel = put_at(linha_digitavel, 19, dv2)
        # linha_digitavel = put_at(linha_digitavel, 9, dv1)
        #
        # return apply_mask(linha_digitavel, self.mascara)
    
