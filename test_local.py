"""
Script para testar o serviço localmente
"""
import requests
import base64
from pathlib import Path

# URL do serviço (ajustar conforme necessário)
BASE_URL = "http://localhost:5000"

def test_health():
    """Testa health check"""
    print("🔍 Testando health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")

def test_upload_sample_image():
    """Testa upload com imagem de exemplo (pixel vermelho 1x1)"""
    print("📤 Testando upload de imagem...")
    
    # Imagem base64 de exemplo (pixel vermelho 1x1)
    sample_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg=="
    
    response = requests.post(
        f"{BASE_URL}/upload",
        json={"image_base64": sample_base64}
    )
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {data}\n")
    
    if data.get("success"):
        image_url = data["image_url"]
        print(f"✅ Imagem disponível em: {image_url}")
        
        # Testar acesso à imagem
        print("🔍 Testando acesso à imagem...")
        img_response = requests.get(image_url)
        print(f"Status: {img_response.status_code}")
        print(f"Content-Type: {img_response.headers.get('Content-Type')}")
        print(f"Size: {len(img_response.content)} bytes\n")
        
        return data["filename"]
    
    return None

def test_stats():
    """Testa endpoint de estatísticas"""
    print("📊 Testando estatísticas...")
    response = requests.get(f"{BASE_URL}/stats")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")

def test_delete(filename):
    """Testa deleção de imagem"""
    if not filename:
        print("⚠️ Nenhuma imagem para deletar\n")
        return
    
    print(f"🗑️ Testando deleção de {filename}...")
    response = requests.delete(f"{BASE_URL}/delete/{filename}")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 TESTE DO INSTAGRAM IMAGE SERVER")
    print("=" * 60 + "\n")
    
    try:
        test_health()
        filename = test_upload_sample_image()
        test_stats()
        test_delete(filename)
        
        print("✅ Todos os testes concluídos!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Erro: Não foi possível conectar ao servidor")
        print("   Certifique-se de que o servidor está rodando:")
        print("   python app.py")
    except Exception as e:
        print(f"❌ Erro: {e}")
