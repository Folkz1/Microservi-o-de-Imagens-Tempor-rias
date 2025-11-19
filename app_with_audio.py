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
IMAGE_EXPIRY_HOURS = 24  # Imagens expiram em 24h
AUDIO_EXPIRY_DAYS = 30  # Áudios expiram em 30 dias
CLEANUP_INTERVAL_MINUTES = 60  # Limpar a cada 1h

# Obter URL base do ambiente ou usar padrão
BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")


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
    
    total_size = sum(f.stat().st_size for f in images + audios)
    
    return jsonify({
        "total_images": len(images),
        "total_audios": len(audios),
        "total_files": len(images) + len(audios),
        "total_size_mb": round(total_size / (1024 * 1024), 2),
        "image_expiry_hours": IMAGE_EXPIRY_HOURS,
        "audio_expiry_days": AUDIO_EXPIRY_DAYS,
        "cleanup_interval_minutes": CLEANUP_INTERVAL_MINUTES
    })


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"🚀 Media Server rodando na porta {port}")
    print(f"📁 Arquivos salvos em: {UPLOAD_FOLDER.absolute()}")
    print(f"🖼️  Imagens expiram em: {IMAGE_EXPIRY_HOURS}h")
    print(f"🎧 Áudios expiram em: {AUDIO_EXPIRY_DAYS} dias")
    print(f"🧹 Limpeza automática a cada {CLEANUP_INTERVAL_MINUTES} minutos")
    app.run(host="0.0.0.0", port=port, debug=False)
