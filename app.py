from flask import Flask, render_template,request, redirect, url_for
import json
import os

app = Flask(__name__)

with open('/home/biblos/site/pdf_files.json') as f:
    pdf_files = json.load(f)

@app.route('/')
def index():
    return render_template('index.html', pdf_files=pdf_files)

@app.route('/sobre')
def sobre():
    return render_template('sobre.html', pdf_files=pdf_files)

# Rota para contribuir com um livro
@app.route('/contribuir', methods=['GET'])
def contribuir():
    return render_template('contribuir.html', pdf_files=pdf_files)

@app.route('/contribuir', methods=['POST'])
def contribuir_post():
    arquivo = request.files['arquivo']
    nome_arquivo = arquivo.filename
    arquivo.save(os.path.join('static/pdf', nome_arquivo))
    return render_template('contribuir_sucesso.html', titulo=nome_arquivo)

if __name__ == '__main__':
    app.run()
