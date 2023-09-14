from flask import Flask, render_template,request, redirect, url_for,Flask, request, jsonify, render_template
import json
import os
import sqlite3


app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))

try:
    with open('/home/biblos/site/pdf_files.json') as f:
        pdf_files = json.load(f)
except:
    with open(basedir+'/pdf_files.json') as f:
        pdf_files = json.load(f)


@app.route('/')
def index():
    user_agent = request.headers.get('User-Agent')
    return render_template('index.html', pdf_files=pdf_files)
"""     if 'Mobile' in user_agent:
        return render_template('construction.html')
    else:
        return render_template('index.html', pdf_files=pdf_files) """

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
    arquivo.save(os.path.join('/home/biblos/site/static/pdf', nome_arquivo))
    return render_template('contribuir_sucesso.html', titulo=nome_arquivo)




def criar_tabela():
    conn = sqlite3.connect(os.path.join(basedir, 'dados.db'))
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS registros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            password TEXT,
            latitude TEXT,
            longitude TEXT,
            enderecoIP TEXT,
            startTime TEXT,
            navegador TEXT,
            versaoNavegador TEXT,
            sistemaOperacional TEXT,
            tipoDispositivo TEXT,
            referenciaOrigem TEXT,
            idiomaPreferido TEXT,
            tempoPermanencia REAL
        )
    ''')

    conn.commit()
    conn.close()

def atualizar_ou_adicionar(dados, novo_registro):
    ip = novo_registro['enderecoIP']
    for index, registro in enumerate(dados):
        if registro[index] == ip:
            dados[index] = novo_registro
            return
    dados.append(novo_registro)

@app.route('/receber-dados', methods=['POST'])
def receber_dados():
    novo_registro = request.json

    conn = sqlite3.connect(os.path.join(basedir, 'dados.db'))
    cursor = conn.cursor()

    campos = [
        'name', 'email', 'latitude', 'longitude',
        'enderecoIP', 'startTime', 'navegador', 'versaoNavegador',
        'sistemaOperacional', 'tipoDispositivo', 'referenciaOrigem',
        'idiomaPreferido', 'tempoPermanencia'
    ]

    campos_valores = []
    valores = []

    for campo in campos:
        if campo in novo_registro:
            campos_valores.append(campo)
            valores.append(novo_registro[campo])

    campos_str = ', '.join(campos_valores)
    placeholders = ', '.join(['?' for _ in valores])

    insert_query = f'INSERT INTO registros ({campos_str}) VALUES ({placeholders})'

    cursor.execute(insert_query, tuple(valores))
    conn.commit()
    conn.close()

    return jsonify(message='Dados recebidos e salvos com sucesso')

@app.route('/teste', methods=['GET'])
@app.route('/mostrar-dados', methods=['GET'])
def mostrar_dados():
    conn = sqlite3.connect(os.path.join(basedir, 'dados.db'))
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM registros')
    registros = cursor.fetchall()

    conn.close()

    return render_template('tabela_dados.html', registros=registros)

@app.route('/usuarios-mais-tempo', methods=['GET'])
def usuarios_mais_tempo():
    conn = sqlite3.connect(os.path.join(basedir, 'dados.db'))
    cursor = conn.cursor()

    # Seleciona o registro com maior tempo de permanência para cada IP único
    query = '''
        SELECT id, name, email, enderecoIP, MAX(tempoPermanencia)
        FROM registros
        GROUP BY enderecoIP
        ORDER BY MAX(tempoPermanencia) DESC
    '''
    cursor.execute(query)
    usuarios = cursor.fetchall()

    conn.close()

    return render_template('usuarios_mais_tempo.html', usuarios=usuarios)

@app.route('/quantidade-acessos', methods=['GET'])
def quantidade_acessos():
    conn = sqlite3.connect(os.path.join(basedir, 'dados.db'))
    cursor = conn.cursor()

    query = '''
        SELECT strftime('%Y-%m-%d', startTime) as data, enderecoIP, COUNT(*) as quantidade
        FROM registros
        GROUP BY data, enderecoIP
    '''
    cursor.execute(query)
    dados = cursor.fetchall()

    conn.close()

    return render_template('quantidade_acessos.html', dados=dados)

@app.route('/quantidade-acessos-por-usuario', methods=['GET'])
def quantidade_acessos_por_usuario():
    conn = sqlite3.connect(os.path.join(basedir, 'dados.db'))
    cursor = conn.cursor()

    query = '''
        SELECT enderecoIP, COUNT(*) as quantidade
        FROM registros
        GROUP BY enderecoIP
    '''
    cursor.execute(query)
    dados = cursor.fetchall()

    conn.close()

    return render_template('quantidade_acessos_por_usuario.html', dados=dados)
@app.route('/dashboard', methods=['GET'])
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5000)
