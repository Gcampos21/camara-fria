from flask import Flask, render_template, request, redirect, jsonify
from datetime import datetime

from services.estoque_service import (
    buscar_produto,
    calcular_estoque,
    obter_mapa,
    buscar_movimentacoes_por_codigo,
    registrar_movimentacao
)

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


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


@app.route("/mapa")
def mapa():
    posicoes = obter_mapa()
    return render_template("mapa.html", posicoes=posicoes)


@app.route("/consulta")
def consulta():
    return render_template("consulta.html")


@app.route("/buscar", methods=["POST"])
def buscar():
    codigo = request.form.get("codigo")

    if not codigo:
        return "Código obrigatório"

    produto = buscar_produto(codigo)

    if not produto:
        return render_template("consulta.html", erro="Produto não encontrado")

    estoque, posicoes = buscar_movimentacoes_por_codigo(codigo)

    return render_template(
        "consulta.html",
        produto=produto,
        codigo=codigo,
        estoque=estoque,
        posicoes=posicoes
    )

from flask import session

app.secret_key = "chave_super_secreta"
def protegido():
    return "usuario" in session
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form.get("usuario")
        senha = request.form.get("senha")

        if usuario == "admin" and senha == "123":
            session["usuario"] = usuario
            return redirect("/")

        return render_template("login.html", erro="Login inválido")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/dashboard")
def dashboard():
    if not protegido():
        return redirect("/login")

    entrada, saida = resumo_estoque()

    return render_template("dashboard.html",
        entrada=entrada,
        saida=saida,
        saldo=entrada - saida
    )

@app.route("/movimentar", methods=["POST"])
def movimentar():

    tipo = request.form.get("tipo")
    codigo = request.form.get("codigo")
    qtd = request.form.get("quantidade")

    if not codigo or not qtd:
        return "Dados obrigatórios não informados"

    try:
        quantidade = int(qtd)
    except:
        return "Quantidade inválida"

    produto = buscar_produto(codigo)

    if not produto:
        return "Produto não encontrado"

    endereco = ""
    validade = ""

    if tipo == "Entrada":
        setor = request.form.get("setor")
        rua = request.form.get("rua")
        posicao = request.form.get("posicao")
        andar = request.form.get("andar")

        endereco = f"{setor}-{rua}-{posicao}-{andar}"
        validade = request.form.get("validade")

        if not validade:
            return "Informe a validade"

    elif tipo == "Saída":
        estoque = calcular_estoque(codigo)

        if quantidade > estoque:
            return "Estoque insuficiente"

    dados = [
        datetime.now(),
        tipo,
        endereco,
        codigo,
        produto,
        quantidade,
        validade
    ]

    registrar_movimentacao(dados)

    return redirect("/")
def listar_movimentacoes():
    wb = abrir_planilha()
    sheet = wb["MOVIMENTACOES"]

    dados = []

    for row in sheet.iter_rows(min_row=2, values_only=True):
        dados.append(row)

    return dados
    @app.route("/historico")
def historico():
    if not protegido():
        return redirect("/login")

    dados = listar_movimentacoes()
    return render_template("historico.html", dados=dados)

if __name__ == "__main__":
    app.run(debug=True)