from flask import Flask, jsonify, request, render_template
from datetime import datetime
import json
import os

app = Flask(__name__)

ARQUIVO_LOG = 'logs.json'

def iniciar_arquivo_log():
    """Cria o arquivo de logs se não existir"""
    if not os.path.exists(ARQUIVO_LOG):
        with open(ARQUIVO_LOG, 'w') as f:
            json.dump([], f)

def obter_ip_real():
    """Obtém o IP real do cliente, mesmo atrás de proxy"""
    # Verifica o cabeçalho X-Forwarded-For (comum em proxies como Render)
    if 'X-Forwarded-For' in request.headers:
        ips = request.headers['X-Forwarded-For'].split(',')
        return ips[0].strip()  # O primeiro IP é o cliente real
    return request.remote_addr

def salvar_log(ip, latitude=None, longitude=None):
    """Salva uma nova entrada de log com tratamento de erros"""
    entrada = {
        "data_hora": datetime.now().isoformat(),
        "ip": ip,
        "latitude": latitude,
        "longitude": longitude,
        "navegador": request.headers.get('User-Agent', 'Desconhecido'),
        "metodo": request.method,
        "endpoint": request.path
    }

    try:
        # Ler logs existentes
        logs = []
        if os.path.exists(ARQUIVO_LOG):
            try:
                with open(ARQUIVO_LOG, 'r') as f:
                    logs = json.load(f)
                    if not isinstance(logs, list):
                        logs = []
            except (json.JSONDecodeError, IOError):
                logs = []

        # Adicionar nova entrada
        logs.append(entrada)

        # Salvar no arquivo
        with open(ARQUIVO_LOG, 'w') as f:
            json.dump(logs, f, indent=2)
            
        return True
    except Exception as e:
        print(f"Falha ao salvar log: {str(e)}")
        return False

@app.route('/')
def inicio():
    return render_template('index.html')

@app.route('/conteudo')
def conteudo():
    return render_template('conteudo.html')

@app.route('/localizacao', methods=['POST'])
def receber_localizacao():
    try:
        dados = request.get_json()
        if not dados:
            return jsonify({"erro": "Nenhum dado fornecido"}), 400

        ip = obter_ip_real()
        latitude = dados.get('latitude')
        longitude = dados.get('longitude')

        if not all([latitude, longitude]):
            return jsonify({"erro": "Dados de localização incompletos"}), 400

        if salvar_log(ip, latitude, longitude):
            return jsonify({"status": "sucesso"})
        else:
            return jsonify({"erro": "Falha ao salvar localização"}), 500

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/logs', methods=['GET'])
def visualizar_logs():
    try:
        if not os.path.exists(ARQUIVO_LOG):
            return jsonify({"erro": "Nenhum log disponível"}), 404

        with open(ARQUIVO_LOG, 'r') as f:
            logs = json.load(f)
            return jsonify(logs)
    except json.JSONDecodeError:
        return jsonify({"erro": "Arquivo de log corrompido"}), 500
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == '__main__':
    iniciar_arquivo_log()  # Garante que o arquivo de log existe
    porta = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=porta)
