from flask import Flask, render_template, request, redirect, url_for, flash, make_response
from utils.parser_factory import get_parser
from werkzeug.utils import secure_filename
from weasyprint import HTML
import os
import json

app = Flask(__name__)
app.secret_key = 'docswitch2025'

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"txt"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def arquivo_permitido(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/analisar", methods=["POST"])
def analisar():
    cliente = request.form.get("cliente")
    fabricante = request.form.get("fabricante")
    arquivo = request.files.get("arquivo")

    if not cliente or not fabricante or not arquivo:
        flash("Todos os campos são obrigatórios.")
        return redirect(url_for("index"))

    if not arquivo_permitido(arquivo.filename):
        flash("Somente arquivos .txt são permitidos.")
        return redirect(url_for("index"))

    nome_seguro = secure_filename(arquivo.filename)
    caminho = os.path.join(app.config["UPLOAD_FOLDER"], nome_seguro)
    arquivo.save(caminho)

    with open(caminho, 'r', encoding='utf-8', errors='ignore') as f:
        config_texto = f.read()

    parser = get_parser(fabricante, config_texto)
    resultado = parser.parse_all()

    return render_template("resultado.html", cliente=cliente, resultado=resultado)

@app.route("/exportar/<formato>", methods=["POST"])
def exportar(formato):
    cliente = request.form.get("cliente")
    resultado = json.loads(request.form.get("resultado"))

    rendered = render_template("resultado.html", cliente=cliente, resultado=resultado)

    if formato == "html":
        response = make_response(rendered)
        response.headers['Content-Type'] = 'text/html'
        response.headers['Content-Disposition'] = f'attachment; filename=analise_{cliente}.html'
        return response

    elif formato == "pdf":
        pdf = HTML(string=rendered).write_pdf()
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=analise_{cliente}.pdf'
        return response

    return "Formato inválido", 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
