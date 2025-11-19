"""
Microserviço para servir imagens e áudios como URLs públicas
Usado para integração com Instagram API e relatórios de chamadas
"""
import os
import base64
import hashlib
import time
from datetime import datetime, timedelta
from pathlib import Path
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import threading
import requests

app = Flask(__name__)
CORS(app)

# Configurações
UPLOAD_FOLDER = Path("temp_files")
UPLOAD_FOLDER.mkdir(exist_ok=True)
CELEBRITY_FOLDER = Path("celebrity_images")
CELEBRITY_FOLDER.mkdir(exist_ok=True)
IMAGE_EXPIRY_HOURS = 24  # Imagens expiram em 24h
AUDIO_EXPIRY_DAYS = 30  # Áudios expiram em 30 dias
CLEANUP_INTERVAL_MINUTES = 60  # Limpar a cada 1h

# Obter URL base do ambiente ou usar padrão
BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")

# Arquivo de mapeamento de celebridades
CELEBRITY_MAPPING_FILE = Path("celebrity_mapping.json")

import json

def load_celebrity_mapping():
    """Carrega mapeamento de celebridades"""
    if CELEBRITY_MAPPING_FILE.exists():
        with open(CELEBRITY_MAPPING_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_celebrity_mapping(mapping):
    """Salva mapeamento de celebridades"""
    with open(CELEBRITY_MAPPING_FILE, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)


def cleanup_old_files():
    """Remove arquivos antigos baseado no tipo"""
    while True:
        try:
            now = time.time()
            deleted_count = 0
            
            # Limpar imagens (24h)
            image_expiry = now - (IMAGE_EXPIRY_HOURS * 3600)
            for image_file in UPLOAD_FOLDER.glob("*.jpg"):
                if image_file.stat().st_mtime < image_expiry:
                    image_file.unlink()
                    deleted_count += 1
            
            # Limpar áudios (30 dias)
            audio_expiry = now - (AUDIO_EXPIRY_DAYS * 24 * 3600)
            for audio_file in UPLOAD_FOLDER.glob("*.mp3"):
                if audio_file.stat().st_mtime < audio_expiry:
                    audio_file.unlink()
                    deleted_count += 1
            
            if deleted_count > 0:
                print(f"🧹 Limpeza: {deleted_count} arquivos antigos removidos")
            
        except Exception as e:
            print(f"❌ Erro na limpeza: {e}")
        
        time.sleep(CLEANUP_INTERVAL_MINUTES * 60)


# Iniciar thread de limpeza
cleanup_thread = threading.Thread(target=cleanup_old_files, daemon=True)
cleanup_thread.start()


@app.route("/health", methods=["GET"])
def health():
    """Health check"""
    image_count = len(list(UPLOAD_FOLDER.glob("*.jpg")))
    audio_count = len(list(UPLOAD_FOLDER.glob("*.mp3")))
    return jsonify({
        "status": "healthy",
        "service": "media-server",
        "images_stored": image_count,
        "audios_stored": audio_count,
        "image_expiry_hours": IMAGE_EXPIRY_HOURS,
        "audio_expiry_days": AUDIO_EXPIRY_DAYS
    })


@app.route("/upload/image", methods=["POST"])
def upload_image():
    """
    Recebe base64, salva e retorna URL pública
    
    Body:
    {
        "image_base64": "data:image/jpeg;base64,/9j/4AAQ..." ou "/9j/4AAQ..."
    }
    """
    try:
        data = request.get_json()
        
        if not data or "image_base64" not in data:
            return jsonify({
                "success": False,
                "error": "Campo 'image_base64' é obrigatório"
            }), 400
        
        image_base64 = data["image_base64"]
        
        if "base64," in image_base64:
            image_base64 = image_base64.split("base64,")[1]
        
        try:
            image_data = base64.b64decode(image_base64)
        except Exception as e:
            return jsonify({
                "success": False,
                "error": f"Base64 inválido: {str(e)}"
            }), 400
        
        image_hash = hashlib.md5(image_data).hexdigest()
        filename = f"{image_hash}.jpg"
        filepath = UPLOAD_FOLDER / filename
        
        with open(filepath, "wb") as f:
            f.write(image_data)
        
        expires_at = datetime.utcnow() + timedelta(hours=IMAGE_EXPIRY_HOURS)
        image_url = f"{BASE_URL}/file/{filename}"
        
        return jsonify({
            "success": True,
            "url": image_url,
            "filename": filename,
            "size_bytes": len(image_data),
            "expires_at": expires_at.isoformat() + "Z"
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/upload/audio", methods=["POST"])
def upload_audio():
    """
    Recebe áudio (base64 ou URL) e retorna URL pública
    
    Body (opção 1 - base64):
    {
        "audio_base64": "base64_string",
        "conversation_id": "conv_123" (opcional)
    }
    
    Body (opção 2 - URL):
    {
        "audio_url": "https://api.elevenlabs.io/...",
        "api_key": "sk_...",
        "conversation_id": "conv_123" (opcional)
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "Body JSON é obrigatório"
            }), 400
        
        audio_data = None
        conversation_id = data.get("conversation_id", "")
        
        # Opção 1: Base64
        if "audio_base64" in data:
            audio_base64 = data["audio_base64"]
            
            if "base64," in audio_base64:
                audio_base64 = audio_base64.split("base64,")[1]
            
            try:
                audio_data = base64.b64decode(audio_base64)
            except Exception as e:
                return jsonify({
                    "success": False,
                    "error": f"Base64 inválido: {str(e)}"
                }), 400
        
        # Opção 2: URL (baixar da API)
        elif "audio_url" in data:
            audio_url = data["audio_url"]
            headers = {}
            
            if "api_key" in data:
                headers["xi-api-key"] = data["api_key"]
            
            try:
                response = requests.get(audio_url, headers=headers, timeout=30)
                response.raise_for_status()
                audio_data = response.content
            except Exception as e:
                return jsonify({
                    "success": False,
                    "error": f"Erro ao baixar áudio: {str(e)}"
                }), 400
        
        else:
            return jsonify({
                "success": False,
                "error": "Forneça 'audio_base64' ou 'audio_url'"
            }), 400
        
        # Gerar nome único
        audio_hash = hashlib.md5(audio_data).hexdigest()
        
        # Usar conversation_id no nome se fornecido
        if conversation_id:
            filename = f"{conversation_id}_{audio_hash[:8]}.mp3"
        else:
            filename = f"{audio_hash}.mp3"
        
        filepath = UPLOAD_FOLDER / filename
        
        # Salvar áudio
        with open(filepath, "wb") as f:
            f.write(audio_data)
        
        # Calcular expiração (30 dias)
        expires_at = datetime.utcnow() + timedelta(days=AUDIO_EXPIRY_DAYS)
        audio_url = f"{BASE_URL}/file/{filename}"
        
        return jsonify({
            "success": True,
            "url": audio_url,
            "filename": filename,
            "size_bytes": len(audio_data),
            "size_mb": round(len(audio_data) / (1024 * 1024), 2),
            "expires_at": expires_at.isoformat() + "Z",
            "expires_in_days": AUDIO_EXPIRY_DAYS
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/file/<filename>", methods=["GET"])
def serve_file(filename):
    """Serve arquivo publicamente (imagem ou áudio)"""
    try:
        filepath = UPLOAD_FOLDER / filename
        
        if not filepath.exists():
            return jsonify({
                "success": False,
                "error": "Arquivo não encontrado ou expirado"
            }), 404
        
        # Determinar mimetype
        if filename.endswith(".jpg") or filename.endswith(".jpeg"):
            mimetype = "image/jpeg"
        elif filename.endswith(".mp3"):
            mimetype = "audio/mpeg"
        else:
            mimetype = "application/octet-stream"
        
        return send_file(filepath, mimetype=mimetype)
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/delete/<filename>", methods=["DELETE"])
def delete_file(filename):
    """Deleta um arquivo manualmente"""
    try:
        filepath = UPLOAD_FOLDER / filename
        
        if not filepath.exists():
            return jsonify({
                "success": False,
                "error": "Arquivo não encontrado"
            }), 404
        
        filepath.unlink()
        
        return jsonify({
            "success": True,
            "message": f"Arquivo {filename} deletado"
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/stats", methods=["GET"])
def stats():
    """Estatísticas do serviço"""
    images = list(UPLOAD_FOLDER.glob("*.jpg"))
    audios = list(UPLOAD_FOLDER.glob("*.mp3"))
    celebrities = list(CELEBRITY_FOLDER.glob("*.jpg"))
    
    total_size = sum(f.stat().st_size for f in images + audios)
    celebrity_size = sum(f.stat().st_size for f in celebrities)
    
    return jsonify({
        "total_images": len(images),
        "total_audios": len(audios),
        "total_celebrities": len(celebrities),
        "total_files": len(images) + len(audios),
        "total_size_mb": round(total_size / (1024 * 1024), 2),
        "celebrity_size_mb": round(celebrity_size / (1024 * 1024), 2),
        "image_expiry_hours": IMAGE_EXPIRY_HOURS,
        "audio_expiry_days": AUDIO_EXPIRY_DAYS,
        "cleanup_interval_minutes": CLEANUP_INTERVAL_MINUTES
    })


# ==================== CELEBRITY MANAGEMENT ====================

@app.route("/admin/celebrities", methods=["GET"])
def admin_page():
    """Página administrativa para gerenciar celebridades"""
    html = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gerenciar Famosos - NutrIA</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 30px;
        }
        .header h1 {
            color: #667eea;
            font-size: 32px;
            margin-bottom: 10px;
        }
        .header p {
            color: #666;
            font-size: 16px;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            text-align: center;
        }
        .stat-card h3 {
            color: #667eea;
            font-size: 36px;
            margin-bottom: 5px;
        }
        .stat-card p {
            color: #666;
            font-size: 14px;
        }
        .upload-section {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 30px;
        }
        .upload-section h2 {
            color: #333;
            margin-bottom: 20px;
            font-size: 24px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            display: block;
            color: #333;
            font-weight: 600;
            margin-bottom: 8px;
            font-size: 14px;
        }
        .form-group input[type="text"] {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        .form-group input[type="text"]:focus {
            outline: none;
            border-color: #667eea;
        }
        .file-input-wrapper {
            position: relative;
            overflow: hidden;
            display: inline-block;
            width: 100%;
        }
        .file-input-wrapper input[type="file"] {
            position: absolute;
            left: -9999px;
        }
        .file-input-label {
            display: block;
            padding: 15px;
            background: #f5f5f5;
            border: 2px dashed #ccc;
            border-radius: 8px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
        }
        .file-input-label:hover {
            background: #e8e8e8;
            border-color: #667eea;
        }
        .file-input-label.has-file {
            background: #e8f5e9;
            border-color: #4caf50;
        }
        .preview-image {
            max-width: 200px;
            max-height: 200px;
            margin-top: 15px;
            border-radius: 8px;
            display: none;
        }
        .btn {
            padding: 12px 30px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        .btn-primary:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }
        .celebrities-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 20px;
        }
        .celebrity-card {
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }
        .celebrity-card:hover {
            transform: translateY(-5px);
        }
        .celebrity-image {
            width: 100%;
            height: 250px;
            object-fit: cover;
        }
        .celebrity-info {
            padding: 15px;
        }
        .celebrity-name {
            font-size: 18px;
            font-weight: 600;
            color: #333;
            margin-bottom: 5px;
        }
        .celebrity-meta {
            font-size: 12px;
            color: #999;
        }
        .celebrity-actions {
            padding: 10px 15px;
            border-top: 1px solid #f0f0f0;
            display: flex;
            gap: 10px;
        }
        .btn-small {
            padding: 6px 12px;
            font-size: 12px;
            flex: 1;
        }
        .btn-danger {
            background: #f44336;
            color: white;
        }
        .btn-danger:hover {
            background: #d32f2f;
        }
        .message {
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: none;
        }
        .message.success {
            background: #e8f5e9;
            color: #2e7d32;
            border: 1px solid #4caf50;
        }
        .message.error {
            background: #ffebee;
            color: #c62828;
            border: 1px solid #f44336;
        }
        .loading {
            display: none;
            text-align: center;
            padding: 20px;
        }
        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎬 Gerenciar Famosos</h1>
            <p>Adicione fotos de celebridades do fitness para usar nos posts do Instagram</p>
        </div>

        <div class="stats" id="stats">
            <div class="stat-card">
                <h3 id="totalCelebrities">0</h3>
                <p>Famosos Cadastrados</p>
            </div>
            <div class="stat-card">
                <h3 id="totalSize">0 MB</h3>
                <p>Espaço Usado</p>
            </div>
        </div>

        <div class="upload-section">
            <h2>➕ Adicionar Novo Famoso</h2>
            
            <div class="message" id="message"></div>
            
            <form id="uploadForm">
                <div class="form-group">
                    <label for="celebrityName">Nome do Famoso *</label>
                    <input type="text" id="celebrityName" placeholder="Ex: Toguro, Julio Balestrin, Paulo Muzy" required>
                </div>

                <div class="form-group">
                    <label for="celebrityAliases">Apelidos (separados por vírgula)</label>
                    <input type="text" id="celebrityAliases" placeholder="Ex: @toguro, toguro maromba">
                </div>

                <div class="form-group">
                    <label>Foto do Famoso * (JPG, PNG, WEBP)</label>
                    <div class="file-input-wrapper">
                        <input type="file" id="celebrityImage" accept="image/*" required>
                        <label for="celebrityImage" class="file-input-label" id="fileLabel">
                            📸 Clique para selecionar uma imagem
                        </label>
                    </div>
                    <img id="previewImage" class="preview-image">
                </div>

                <button type="submit" class="btn btn-primary" id="submitBtn">
                    ✅ Adicionar Famoso
                </button>
            </form>

            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p style="margin-top: 10px; color: #666;">Processando imagem...</p>
            </div>
        </div>

        <div class="upload-section">
            <h2>📋 Famosos Cadastrados</h2>
            <div class="celebrities-grid" id="celebritiesGrid">
                <!-- Preenchido via JavaScript -->
            </div>
        </div>
    </div>

    <script>
        const API_BASE = window.location.origin;

        // Preview de imagem
        document.getElementById('celebrityImage').addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    const preview = document.getElementById('previewImage');
                    preview.src = e.target.result;
                    preview.style.display = 'block';
                    document.getElementById('fileLabel').classList.add('has-file');
                    document.getElementById('fileLabel').innerHTML = `✅ ${file.name}`;
                };
                reader.readAsDataURL(file);
            }
        });

        // Carregar estatísticas
        async function loadStats() {
            try {
                const response = await fetch(`${API_BASE}/api/celebrities`);
                const data = await response.json();
                document.getElementById('totalCelebrities').textContent = data.total;
                document.getElementById('totalSize').textContent = data.total_size_mb + ' MB';
            } catch (error) {
                console.error('Erro ao carregar stats:', error);
            }
        }

        // Carregar lista de celebridades
        async function loadCelebrities() {
            try {
                const response = await fetch(`${API_BASE}/api/celebrities`);
                const data = await response.json();
                
                const grid = document.getElementById('celebritiesGrid');
                
                if (data.celebrities.length === 0) {
                    grid.innerHTML = '<p style="text-align: center; color: #999; padding: 40px;">Nenhum famoso cadastrado ainda. Adicione o primeiro!</p>';
                    return;
                }
                
                grid.innerHTML = data.celebrities.map(celeb => `
                    <div class="celebrity-card">
                        <img src="${celeb.url}" class="celebrity-image" alt="${celeb.full_name}">
                        <div class="celebrity-info">
                            <div class="celebrity-name">${celeb.full_name}</div>
                            <div class="celebrity-meta">
                                ${celeb.aliases.length} apelidos • ${celeb.size_kb} KB
                            </div>
                        </div>
                        <div class="celebrity-actions">
                            <button class="btn btn-small btn-danger" onclick="deleteCelebrity('${celeb.slug}')">
                                🗑️ Deletar
                            </button>
                        </div>
                    </div>
                `).join('');
            } catch (error) {
                console.error('Erro ao carregar celebridades:', error);
            }
        }

        // Upload de novo famoso
        document.getElementById('uploadForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const name = document.getElementById('celebrityName').value.trim();
            const aliasesInput = document.getElementById('celebrityAliases').value.trim();
            const imageFile = document.getElementById('celebrityImage').files[0];
            
            if (!name || !imageFile) {
                showMessage('Preencha todos os campos obrigatórios', 'error');
                return;
            }
            
            // Converter imagem para base64
            const reader = new FileReader();
            reader.onload = async function(e) {
                const base64 = e.target.result;
                
                const aliases = aliasesInput ? aliasesInput.split(',').map(a => a.trim()) : [];
                
                document.getElementById('loading').style.display = 'block';
                document.getElementById('submitBtn').disabled = true;
                
                try {
                    const response = await fetch(`${API_BASE}/api/celebrities`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            name: name,
                            aliases: aliases,
                            image_base64: base64
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        showMessage(`✅ ${name} adicionado com sucesso!`, 'success');
                        document.getElementById('uploadForm').reset();
                        document.getElementById('previewImage').style.display = 'none';
                        document.getElementById('fileLabel').classList.remove('has-file');
                        document.getElementById('fileLabel').innerHTML = '📸 Clique para selecionar uma imagem';
                        loadStats();
                        loadCelebrities();
                    } else {
                        showMessage(`❌ Erro: ${data.error}`, 'error');
                    }
                } catch (error) {
                    showMessage(`❌ Erro: ${error.message}`, 'error');
                } finally {
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('submitBtn').disabled = false;
                }
            };
            reader.readAsDataURL(imageFile);
        });

        // Deletar celebridade
        async function deleteCelebrity(slug) {
            if (!confirm(`Tem certeza que deseja deletar este famoso?`)) {
                return;
            }
            
            try {
                const response = await fetch(`${API_BASE}/api/celebrities/${slug}`, {
                    method: 'DELETE'
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showMessage('✅ Famoso deletado com sucesso!', 'success');
                    loadStats();
                    loadCelebrities();
                } else {
                    showMessage(`❌ Erro: ${data.error}`, 'error');
                }
            } catch (error) {
                showMessage(`❌ Erro: ${error.message}`, 'error');
            }
        }

        // Mostrar mensagem
        function showMessage(text, type) {
            const message = document.getElementById('message');
            message.textContent = text;
            message.className = `message ${type}`;
            message.style.display = 'block';
            setTimeout(() => {
                message.style.display = 'none';
            }, 5000);
        }

        // Carregar dados ao iniciar
        loadStats();
        loadCelebrities();
    </script>
</body>
</html>
    """
    from flask import Response
    return Response(html, mimetype='text/html')


@app.route("/api/celebrities", methods=["GET"])
def list_celebrities():
    """Lista todas as celebridades cadastradas"""
    try:
        mapping = load_celebrity_mapping()
        
        celebrities = []
        for slug, data in mapping.items():
            filepath = CELEBRITY_FOLDER / data['file']
            if filepath.exists():
                size_kb = round(filepath.stat().st_size / 1024, 1)
                celebrities.append({
                    "slug": slug,
                    "full_name": data['full_name'],
                    "aliases": data['aliases'],
                    "url": data['url'],
                    "file": data['file'],
                    "size_kb": size_kb,
                    "cached_at": data.get('cached_at', '')
                })
        
        total_size = sum(c['size_kb'] for c in celebrities)
        
        return jsonify({
            "success": True,
            "total": len(celebrities),
            "total_size_mb": round(total_size / 1024, 2),
            "celebrities": celebrities
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/api/celebrities", methods=["POST"])
def add_celebrity():
    """Adiciona uma nova celebridade"""
    try:
        data = request.get_json()
        
        if not data or "name" not in data or "image_base64" not in data:
            return jsonify({
                "success": False,
                "error": "Campos 'name' e 'image_base64' são obrigatórios"
            }), 400
        
        name = data["name"].strip()
        aliases = data.get("aliases", [])
        image_base64 = data["image_base64"]
        
        # Remove data URI prefix se existir
        if "base64," in image_base64:
            image_base64 = image_base64.split("base64,")[1]
        
        # Decodifica imagem
        try:
            image_data = base64.b64decode(image_base64)
        except Exception as e:
            return jsonify({
                "success": False,
                "error": f"Base64 inválido: {str(e)}"
            }), 400
        
        # Gera slug (nome normalizado)
        slug = name.lower().replace(' ', '_').replace('@', '')
        slug = ''.join(c for c in slug if c.isalnum() or c == '_')
        
        # Nome do arquivo
        filename = f"{slug}.jpg"
        filepath = CELEBRITY_FOLDER / filename
        
        # Salva imagem
        with open(filepath, "wb") as f:
            f.write(image_data)
        
        # Atualiza mapeamento
        mapping = load_celebrity_mapping()
        
        # Adiciona aliases padrão
        all_aliases = [name.lower(), slug]
        if aliases:
            all_aliases.extend([a.lower() for a in aliases])
        all_aliases = list(set(all_aliases))  # Remove duplicatas
        
        mapping[slug] = {
            "file": filename,
            "url": f"{BASE_URL}/celebrity/{slug}",
            "aliases": all_aliases,
            "full_name": name,
            "cached_at": datetime.utcnow().isoformat() + "Z",
            "source": "manual_upload",
            "verified": True
        }
        
        save_celebrity_mapping(mapping)
        
        return jsonify({
            "success": True,
            "slug": slug,
            "url": mapping[slug]["url"],
            "message": f"{name} adicionado com sucesso!"
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/api/celebrities/<slug>", methods=["DELETE"])
def delete_celebrity(slug):
    """Deleta uma celebridade"""
    try:
        mapping = load_celebrity_mapping()
        
        if slug not in mapping:
            return jsonify({
                "success": False,
                "error": "Celebridade não encontrada"
            }), 404
        
        # Deleta arquivo
        filepath = CELEBRITY_FOLDER / mapping[slug]['file']
        if filepath.exists():
            filepath.unlink()
        
        # Remove do mapeamento
        name = mapping[slug]['full_name']
        del mapping[slug]
        save_celebrity_mapping(mapping)
        
        return jsonify({
            "success": True,
            "message": f"{name} deletado com sucesso!"
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/celebrity/<slug>", methods=["GET"])
def get_celebrity_image(slug):
    """Retorna imagem de uma celebridade pelo slug"""
    try:
        mapping = load_celebrity_mapping()
        
        if slug not in mapping:
            return jsonify({
                "success": False,
                "error": "Celebridade não encontrada"
            }), 404
        
        filepath = CELEBRITY_FOLDER / mapping[slug]['file']
        
        if not filepath.exists():
            return jsonify({
                "success": False,
                "error": "Arquivo de imagem não encontrado"
            }), 404
        
        return send_file(filepath, mimetype="image/jpeg")
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/api/celebrity/search", methods=["GET"])
def search_celebrity():
    """Busca celebridade por nome ou alias"""
    try:
        query = request.args.get('q', '').lower().strip()
        
        if not query:
            return jsonify({
                "success": False,
                "error": "Parâmetro 'q' é obrigatório"
            }), 400
        
        mapping = load_celebrity_mapping()
        
        # Busca por slug exato
        if query in mapping:
            return jsonify({
                "success": True,
                "found": True,
                "slug": query,
                "url": mapping[query]['url'],
                "full_name": mapping[query]['full_name']
            })
        
        # Busca por alias
        for slug, data in mapping.items():
            if query in data['aliases']:
                return jsonify({
                    "success": True,
                    "found": True,
                    "slug": slug,
                    "url": data['url'],
                    "full_name": data['full_name']
                })
        
        return jsonify({
            "success": True,
            "found": False,
            "message": f"Celebridade '{query}' não encontrada"
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"🚀 Media Server rodando na porta {port}")
    print(f"📁 Arquivos salvos em: {UPLOAD_FOLDER.absolute()}")
    print(f"🖼️  Imagens expiram em: {IMAGE_EXPIRY_HOURS}h")
    print(f"🎧 Áudios expiram em: {AUDIO_EXPIRY_DAYS} dias")
    print(f"🧹 Limpeza automática a cada {CLEANUP_INTERVAL_MINUTES} minutos")
    app.run(host="0.0.0.0", port=port, debug=False)
