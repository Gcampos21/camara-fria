from flask import Flask, render_template, request, redirect, jsonify
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

# CONEXÃO GOOGLE SHEETS

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    "credenciais.json", scope
)

client = gspread.authorize(creds)

planilha = client.open_by_key("1IL5oZGlpzTCDd9jBV-eKhN1nr8dJJoRLVRYVmNMO6Eo")

aba_produtos = planilha.worksheet("PRODUTOS")
aba_mov = planilha.worksheet("MOVIMENTACOES")


# BUSCAR PRODUTO

def buscar_produto(codigo):

    dados = aba_produtos.get_all_records()

    codigo = str(codigo).strip()

    for linha in dados:

        cod_planilha = str(linha.get("CODIGO", "")).strip()

        if cod_planilha == codigo:

            produto = linha.get("PRODUTO")

            if produto:
                return produto

    return None


# CALCULAR ESTOQUE

def calcular_estoque(codigo):

    dados = aba_mov.get_all_records()

    estoque = 0

    codigo = str(codigo).strip()

    for linha in dados:

        cod_planilha = str(linha.get("CODIGO", "")).strip()

        if cod_planilha == codigo:

            tipo = linha.get("TIPO")
            qtd = int(linha.get("QTD", 0))

            if tipo == "Entrada":
                estoque += qtd

            if tipo == "Saída":
                estoque -= qtd

    return estoque

# API BUSCA AUTOMÁTICA

@app.route("/produto/<codigo>")
def produto_api(codigo):

    produto = buscar_produto(codigo)

    if not produto:
        return jsonify({"produto": "", "estoque": 0})

    estoque = calcular_estoque(codigo)

    return jsonify({
        "produto": produto,
        "estoque": estoque
    })


# MAPA DA CÂMARA

@app.route("/mapa")
def mapa():

    dados = aba_mov.get_all_records()

    posicoes = {}

    for linha in dados:

        tipo = linha["TIPO"]
        endereco = linha["ENDERECO"]
        produto = linha["PRODUTO"]
        qtd = int(linha["QTD"])
        validade = linha["VALIDADE"]

        if not endereco:
            continue

        if endereco not in posicoes:

            posicoes[endereco] = {
                "produto": produto,
                "qtd": 0,
                "validade": validade
            }

        if tipo == "Entrada":
            posicoes[endereco]["qtd"] += qtd

        if tipo == "Saída":
            posicoes[endereco]["qtd"] -= qtd

    return render_template("mapa.html", posicoes=posicoes)


# CONSULTA

@app.route("/consulta")
def consulta():
    return render_template("consulta.html")


@app.route("/buscar", methods=["POST"])
def buscar():

    codigo = request.form["codigo"]

    dados = aba_mov.get_all_records()

    estoque_total = 0
    posicoes = {}

    for linha in dados:

        if str(linha["CODIGO"]).strip() == str(codigo).strip():

            tipo = linha["TIPO"]
            endereco = linha["ENDERECO"]
            qtd = int(linha["QTD"])

            if tipo == "Entrada":

                estoque_total += qtd

                if endereco not in posicoes:
                    posicoes[endereco] = 0

                posicoes[endereco] += qtd

            if tipo == "Saída":

                estoque_total -= qtd

    produto = buscar_produto(codigo)

    return render_template(
        "consulta.html",
        produto=produto,
        codigo=codigo,
        estoque=estoque_total,
        posicoes=posicoes
    )


# TELA PRINCIPAL

@app.route("/")
def index():
    return render_template("index.html")


# MOVIMENTAÇÃO

@app.route("/movimentar", methods=["POST"])
def movimentar():

    tipo = request.form["tipo"]
    codigo = request.form["codigo"]

    qtd = request.form.get("quantidade")

    if not qtd:
        return "Informe a quantidade"

    quantidade = int(qtd)

    produto = buscar_produto(codigo)

    if not produto:
        return "Produto não encontrado"

    endereco = ""
    validade = ""

    if tipo == "Entrada":

        setor = request.form["setor"]
        rua = request.form["rua"]
        posicao = request.form["posicao"]
        andar = request.form["andar"]

        endereco = f"{setor}-{rua}-{posicao}-{andar}"

        validade = request.form.get("validade")

        if not validade:
            return "Informe a validade"

    if tipo == "Saída":

        estoque = calcular_estoque(codigo)

        if quantidade > estoque:
            return "Estoque insuficiente"

    aba_mov.append_row([
        str(datetime.now()),
        tipo,
        endereco,
        codigo,
        produto,
        quantidade,
        validade
    ])

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)