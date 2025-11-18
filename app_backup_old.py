"""
Microserviço para servir imagens base64 como URLs públicas
Usado para integração com Instagram API
BACKUP DA VERSÃO ANTIGA - SÓ IMAGENS
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

app = Flask(__name__)
CORS(app)

# Configurações
UPLOAD_FOLDER = Path("temp_images")
UPLOAD_FOLDER.mkdir(exist_ok=True)
IMAGE_EXPIRY_HOURS = 24  # Imagens expiram em 24h
CLEANUP_INTERVAL_MINUTES = 60  # Limpar a cada 1h

# Obter URL base do ambiente ou usar padrão
BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")


def cleanup_old_images():
    """Remove imagens mais antigas que IMAGE_EXPIRY_HOURS"""
    while True:
        try:
            now = time.time()
            expiry_time = now - (IMAGE_EXPIRY_HOURS * 3600)
            
            deleted_count = 0
            for image_file in UPLOAD_FOLDER.glob("*.jpg"):
                if image_file.stat().st_mtime < expiry_time:
                    image_file.unlink()
                    deleted_count += 1
            
            if deleted_count > 0:
                print(f"🧹 Limpeza: {deleted_count} imagens antigas removidas")
            
        except Exception as e:
            print(f"❌ Erro na limpeza: {e}")
        
        # Aguardar próximo ciclo
        time.sleep(CLEANUP_INTERVAL_MINUTES * 60)


# Iniciar thread de limpeza
cleanup_thread = threading.Thread(target=cleanup_old_images, daemon=True)
cleanup_thread.start()


@app.route("/health", methods=["GET"])
def health():
    """Health check"""
    image_count = len(list(UPLOAD_FOLDER.glob("*.jpg")))
    return jsonify({
        "status": "healthy",
        "service": "instagram-image-server",
        "images_stored": image_count,
        "expiry_hours": IMAGE_EXPIRY_HOURS
    })


@app.route("/upload", methods=["POST"])
def upload_image():
    """
    Recebe base64, salva e retorna URL pública
    
    Body:
    {
        "image_base64": "data:image/jpeg;base64,/9j/4AAQ..." ou "/9j/4AAQ..."
    }
    
    Response:
    {
        "success": true,
        "image_url": "https://seu-dominio.com/image/abc123.jpg",
        "expires_at": "2024-11-19T10:00:00Z"
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
        
        # Remover prefixo data:image se existir
        if "base64," in image_base64:
            image_base64 = image_base64.split("base64,")[1]
        
        # Decodificar base64
        try:
            image_data = base64.b64decode(image_base64)
        except Exception as e:
            return jsonify({
                "success": False,
                "error": f"Base64 inválido: {str(e)}"
            }), 400
        
        # Gerar nome único baseado no hash do conteúdo
        image_hash = hashlib.md5(image_data).hexdigest()
        filename = f"{image_hash}.jpg"
        filepath = UPLOAD_FOLDER / filename
        
        # Salvar imagem
        with open(filepath, "wb") as f:
            f.write(image_data)
        
        # Calcular data de expiração
        expires_at = datetime.utcnow() + timedelta(hours=IMAGE_EXPIRY_HOURS)
        
        # Retornar URL pública
        image_url = f"{BASE_URL}/image/{filename}"
        
        return jsonify({
            "success": True,
            "image_url": image_url,
            "filename": filename,
            "size_bytes": len(image_data),
            "expires_at": expires_at.isoformat() + "Z"
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/image/<filename>", methods=["GET"])
def serve_image(filename):
    """Serve a imagem publicamente"""
    try:
        filepath = UPLOAD_FOLDER / filename
        
        if not filepath.exists():
            return jsonify({
                "success": False,
                "error": "Imagem não encontrada ou expirada"
            }), 404
        
        return send_file(filepath, mimetype="image/jpeg")
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/delete/<filename>", methods=["DELETE"])
def delete_image(filename):
    """Deleta uma imagem manualmente (opcional)"""
    try:
        filepath = UPLOAD_FOLDER / filename
        
        if not filepath.exists():
            return jsonify({
                "success": False,
                "error": "Imagem não encontrada"
            }), 404
        
        filepath.unlink()
        
        return jsonify({
            "success": True,
            "message": f"Imagem {filename} deletada"
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
    total_size = sum(img.stat().st_size for img in images)
    
    return jsonify({
        "total_images": len(images),
        "total_size_mb": round(total_size / (1024 * 1024), 2),
        "expiry_hours": IMAGE_EXPIRY_HOURS,
        "cleanup_interval_minutes": CLEANUP_INTERVAL_MINUTES
    })


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"🚀 Instagram Image Server rodando na porta {port}")
    print(f"📁 Imagens salvas em: {UPLOAD_FOLDER.absolute()}")
    print(f"⏰ Expiração: {IMAGE_EXPIRY_HOURS}h")
    print(f"🧹 Limpeza automática a cada {CLEANUP_INTERVAL_MINUTES} minutos")
    app.run(host="0.0.0.0", port=port, debug=False)
