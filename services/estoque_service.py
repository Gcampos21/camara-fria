from datetime import datetime
from services.excel_service import abrir_planilha, salvar_planilha
from utils.helpers import normalizar


def buscar_produto(codigo):
    wb = abrir_planilha(data_only=True)
    sheet = wb["PRODUTOS"]

    codigo = normalizar(codigo)

    for row in sheet.iter_rows(min_row=2):
        cod = normalizar(row[0].value)

        if cod == codigo:
            produto = row[1].value
            return normalizar(produto)

    return None


def calcular_estoque(codigo):
    wb = abrir_planilha()
    sheet = wb["MOVIMENTACOES"]

    estoque = 0

    for row in sheet.iter_rows(min_row=2, values_only=True):
        tipo = row[1]
        cod = normalizar(row[3])
        qtd = row[5] or 0

        if cod == normalizar(codigo):
            if tipo == "Entrada":
                estoque += qtd
            elif tipo == "Saída":
                estoque -= qtd

    return estoque


def obter_mapa():
    wb = abrir_planilha()
    sheet = wb["MOVIMENTACOES"]

    posicoes = {}

    for row in sheet.iter_rows(min_row=2, values_only=True):
        tipo = row[1]
        endereco = row[2]
        produto = row[4]
        qtd = row[5] or 0
        validade = row[6]

        if not endereco:
            continue

        if endereco not in posicoes:
            posicoes[endereco] = {
                "produto": produto,
                "qtd": 0,
                "validade": validade
            }

        if tipo == "Entrada":
            posicoes[endereco]["produto"] = produto
            posicoes[endereco]["validade"] = validade
            posicoes[endereco]["qtd"] += qtd

        elif tipo == "Saída":
            posicoes[endereco]["qtd"] -= qtd

    return posicoes


def buscar_movimentacoes_por_codigo(codigo):
    wb = abrir_planilha()
    sheet = wb["MOVIMENTACOES"]

    estoque_total = 0
    posicoes = {}

    for row in sheet.iter_rows(min_row=2, values_only=True):
        tipo = row[1]
        endereco = row[2]
        cod = normalizar(row[3])
        qtd = row[5] or 0

        if cod == normalizar(codigo):

            if tipo == "Entrada":
                estoque_total += qtd

                if endereco not in posicoes:
                    posicoes[endereco] = 0

                posicoes[endereco] += qtd

            elif tipo == "Saída":
                estoque_total -= qtd

    return estoque_total, posicoes


def registrar_movimentacao(dados):
    wb = abrir_planilha()
    sheet = wb["MOVIMENTACOES"]

    linha = sheet.max_row + 1

    for i, valor in enumerate(dados, start=1):
        sheet.cell(row=linha, column=i).value = valor

    salvar_planilha(wb)

    def resumo_estoque():
    wb = abrir_planilha()
    sheet = wb["MOVIMENTACOES"]

    total_entrada = 0
    total_saida = 0

    for row in sheet.iter_rows(min_row=2, values_only=True):
        tipo = row[1]
        qtd = row[5] or 0

        if tipo == "Entrada":
            total_entrada += qtd
        elif tipo == "Saída":
            total_saida += qtd

    return total_entrada, total_saida