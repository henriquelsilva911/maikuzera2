from flask import Flask, jsonify, request, render_template
from datetime import datetime
import json
import os

app = Flask(__name__)

LOG_FILE = 'logs.json'


def salvar_log(ip):
    agora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log = {"ip": ip, "horario": agora}

    dados = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, 'r') as f:
                dados = json.load(f)
        except json.JSONDecodeError:
            # Se o arquivo estiver vazio ou quebrado, só recomeça a lista
            dados = []

    dados.append(log)

    with open(LOG_FILE, 'w') as f:
        json.dump(dados, f, indent=4)


@app.route('/')
def index():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    salvar_log(ip)
    return render_template('index.html')  # aqui você põe seu HTML

@app.route('/logs', methods=['GET'])
def logs():
    with open(LOG_FILE, 'r') as f:
        logs_data = json.load(f)
    return jsonify(logs_data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81)
