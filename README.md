# 🖼️ Instagram Image Server

Microserviço para converter imagens base64 em URLs públicas para uso com Instagram API.

## 🎯 Funcionalidades

- ✅ Recebe imagem em base64
- ✅ Salva temporariamente (24h)
- ✅ Retorna URL pública
- ✅ Limpeza automática de imagens antigas
- ✅ Health check
- ✅ Estatísticas de uso

## 🚀 Deploy no Easypanel

### 1. Criar novo serviço

```bash
Nome: instagram-image-server
Tipo: Docker
```

### 2. Configurar variáveis de ambiente

```env
BASE_URL=https://instagram-images.seu-dominio.com
PORT=5000
```

### 3. Build e Deploy

O Easypanel vai detectar o Dockerfile automaticamente.

## 📡 Endpoints

### POST /upload

Faz upload de imagem base64 e retorna URL pública.

**Request:**
```json
{
  "image_base64": "data:image/jpeg;base64,/9j/4AAQ..." 
}
```

**Response:**
```json
{
  "success": true,
  "image_url": "https://seu-dominio.com/image/abc123.jpg",
  "filename": "abc123.jpg",
  "size_bytes": 245678,
  "expires_at": "2024-11-19T10:00:00Z"
}
```

### GET /image/{filename}

Serve a imagem publicamente (usado pelo Instagram).

**Exemplo:**
```
https://seu-dominio.com/image/abc123.jpg
```

### GET /health

Health check do serviço.

**Response:**
```json
{
  "status": "healthy",
  "service": "instagram-image-server",
  "images_stored": 42,
  "expiry_hours": 24
}
```

### GET /stats

Estatísticas de uso.

**Response:**
```json
{
  "total_images": 42,
  "total_size_mb": 125.5,
  "expiry_hours": 24,
  "cleanup_interval_minutes": 60
}
```

### DELETE /image/{filename}

Deleta uma imagem manualmente (opcional).

## 🧪 Testar Localmente

```bash
# Instalar dependências
pip install -r requirements.txt

# Rodar servidor
python app.py

# Testar upload
curl -X POST http://localhost:5000/upload \
  -H "Content-Type: application/json" \
  -d '{"image_base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="}'

# Ver stats
curl http://localhost:5000/stats
```

## 🔧 Uso no N8N

### Node: HTTP Request - Upload Imagem

```javascript
// No Code node antes do HTTP Request
const imageBase64 = $json.image_base64;

return {
  json: {
    image_base64: imageBase64
  }
};
```

**HTTP Request Config:**
- Method: POST
- URL: `https://instagram-images.seu-dominio.com/upload`
- Body: JSON
- Body Content: `{{ $json }}`

**Response:**
```javascript
// Extrair URL da resposta
const imageUrl = $json.image_url;
```

## ⚙️ Configurações

Ajuste no `app.py`:

```python
IMAGE_EXPIRY_HOURS = 24  # Tempo de vida das imagens
CLEANUP_INTERVAL_MINUTES = 60  # Frequência de limpeza
```

## 🔒 Segurança

- ✅ CORS habilitado
- ✅ Validação de base64
- ✅ Limpeza automática
- ✅ Nomes únicos (hash MD5)
- ⚠️ Sem autenticação (adicionar se necessário)

## 📊 Monitoramento

```bash
# Ver logs no Easypanel
# Verificar /health periodicamente
# Monitorar /stats para uso de disco
```

## 🐛 Troubleshooting

**Imagem não aparece:**
- Verificar se BASE_URL está correto
- Verificar se imagem não expirou (24h)
- Checar logs do servidor

**Erro 413 (Payload too large):**
- Aumentar limite no nginx/proxy
- Comprimir imagem antes do upload

**Disco cheio:**
- Reduzir IMAGE_EXPIRY_HOURS
- Aumentar CLEANUP_INTERVAL_MINUTES
- Adicionar volume persistente no Easypanel
