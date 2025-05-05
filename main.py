from flask import Flask, jsonify, request, render_template
from datetime import datetime
import json
import os

app = Flask(__name__)

# Configuração robusta do sistema de logs
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
LOG_FILE = os.path.join(LOG_DIR, 'logs.json')

def inicializar_sistema():
    """Configuração inicial do sistema"""
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
        if not os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'w') as f:
                json.dump([], f)
    except Exception as e:
        print(f"ERRO DE INICIALIZAÇÃO: {str(e)}")

def obter_ip_usuario():
    """Obtém o IP real do usuário mesmo com proxy"""
    if 'X-Forwarded-For' in request.headers:
        return request.headers['X-Forwarded-For'].split(',')[0].strip()
    return request.remote_addr

def registrar_log(ip, lat, lng):
    """Registra o acesso com tratamento robusto de erros"""
    try:
        registro = {
            "ip": ip,
            "latitude": lat,
            "longitude": lng,
            "data_hora": datetime.now().isoformat(),
            "user_agent": request.headers.get('User-Agent', '')
        }

        logs = []
        if os.path.exists(LOG_FILE):
            try:
                with open(LOG_FILE, 'r') as f:
                    logs = json.load(f)
            except json.JSONDecodeError:
                logs = []

        logs.append(registro)

        with open(LOG_FILE, 'w') as f:
            json.dump(logs, f, indent=2)

        return True
    except Exception as e:
        print(f"FALHA NO REGISTRO: {str(e)}")
        return False

@app.route('/')
def pagina_inicial():
    return render_template('index.html')

@app.route('/conteudo')
def mostrar_conteudo():
    return render_template('conteudo.html')

@app.route('/api/localizacao', methods=['POST'])
def receber_localizacao():
    try:
        # Verifica se é JSON
        if not request.is_json:
            return jsonify({
                "status": "erro",
                "mensagem": "Formato inválido, use JSON"
            }), 400

        dados = request.get_json()
        ip = obter_ip_usuario()
        lat = dados.get('latitude')
        lng = dados.get('longitude')

        # Validação dos dados
        if None in (lat, lng):
            return jsonify({
                "status": "erro",
                "mensagem": "Coordenadas incompletas"
            }), 400

        if not registrar_log(ip, lat, lng):
            return jsonify({
                "status": "erro",
                "mensagem": "Falha no registro"
            }), 500

        return jsonify({"status": "sucesso"})

    except Exception as e:
        return jsonify({
            "status": "erro",
            "mensagem": f"Erro interno: {str(e)}"
        }), 500

@app.route('/api/logs', methods=['GET'])
def visualizar_logs():
    try:
        if not os.path.exists(LOG_FILE):
            return jsonify({"logs": []})

        with open(LOG_FILE, 'r') as f:
            return jsonify({"logs": json.load(f)})
    except Exception as e:
        return jsonify({
            "status": "erro",
            "mensagem": f"Falha ao ler logs: {str(e)}"
        }), 500

if __name__ == '__main__':
    inicializar_sistema()
    porta = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=porta)
