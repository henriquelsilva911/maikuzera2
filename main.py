from flask import Flask, jsonify, request, render_template, redirect, url_for
from datetime import datetime
import json
import os

app = Flask(__name__)

LOG_FILE = 'logs.json'

def init_log_file():
    """Garante que o arquivo de logs existe e é válido"""
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'w') as f:
            json.dump([], f)

def salvar_log(ip, latitude=None, longitude=None):
    """Salva logs de forma robusta com tratamento de erros"""
    agora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log = {
        "ip": ip,
        "horario": agora,
        "latitude": latitude,
        "longitude": longitude
    }

    try:
        # Ler logs existentes
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'r') as f:
                try:
                    dados = json.load(f)
                    if not isinstance(dados, list):
                        dados = []
                except json.JSONDecodeError:
                    dados = []
        else:
            dados = []

        # Adicionar novo log
        dados.append(log)

        # Salvar de volta
        with open(LOG_FILE, 'w') as f:
            json.dump(dados, f, indent=4)

    except Exception as e:
        print(f"Erro ao salvar log: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/conteudo')
def conteudo():
    return render_template('conteudo.html')

@app.route('/logs', methods=['GET'])
def get_logs():
    try:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'r') as f:
                logs_data = json.load(f)
            return jsonify(logs_data)
        return jsonify([])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/location', methods=['POST'])
def save_location():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    data = request.get_json()

    try:
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        salvar_log(ip, latitude, longitude)
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

if __name__ == '__main__':
    init_log_file()  # Garante que o arquivo de logs existe
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)