# 🎧 Atualização do Microserviço - Suporte a Áudios

## 📋 O que mudou?

O microserviço agora suporta:
- ✅ Imagens (24h de expiração)
- ✅ Áudios (30 dias de expiração)
- ✅ Upload via base64 ou URL
- ✅ Limpeza automática por tipo de arquivo

## 🚀 Como Atualizar

### Opção 1: Substituir arquivo (Recomendado)

```bash
# Backup do arquivo antigo
cp app.py app_old.py

# Renomear novo arquivo
mv app_with_audio.py app.py

# Reiniciar serviço
# Se estiver usando systemd, docker, etc
```

### Opção 2: Deploy novo (Easypanel/Docker)

Se estiver usando Easypanel ou Docker, apenas faça o deploy com o novo `app.py`

## 📝 Novos Endpoints

### 1. Upload de Áudio via URL (Recomendado para n8n)

```bash
POST /upload/audio
Content-Type: application/json

{
  "audio_url": "https://api.elevenlabs.io/v1/convai/conversations/conv_123/audio",
  "api_key": "sk_...",
  "conversation_id": "conv_123"
}
```

**Resposta:**
```json
{
  "success": true,
  "url": "https://seu-microservico.com/file/conv_123_abc12345.mp3",
  "filename": "conv_123_abc12345.mp3",
  "size_bytes": 245678,
  "size_mb": 0.23,
  "expires_at": "2025-12-18T00:00:00Z",
  "expires_in_days": 30
}
```

### 2. Upload de Áudio via Base64

```bash
POST /upload/audio
Content-Type: application/json

{
  "audio_base64": "base64_string_here",
  "conversation_id": "conv_123"
}
```

### 3. Servir Arquivo (Imagem ou Áudio)

```bash
GET /file/{filename}
```

Retorna o arquivo com mimetype correto:
- `.jpg` → `image/jpeg`
- `.mp3` → `audio/mpeg`

### 4. Health Check Atualizado

```bash
GET /health
```

**Resposta:**
```json
{
  "status": "healthy",
  "service": "media-server",
  "images_stored": 5,
  "audios_stored": 12,
  "image_expiry_hours": 24,
  "audio_expiry_days": 30
}
```

### 5. Estatísticas

```bash
GET /stats
```

**Resposta:**
```json
{
  "total_images": 5,
  "total_audios": 12,
  "total_files": 17,
  "total_size_mb": 45.67,
  "image_expiry_hours": 24,
  "audio_expiry_days": 30,
  "cleanup_interval_minutes": 60
}
```

## 🔧 Configuração

### Variáveis de Ambiente

```bash
# URL base do serviço (obrigatório)
BASE_URL=https://seu-microservico.com

# Porta (opcional, padrão: 5000)
PORT=5000
```

### Estrutura de Pastas

```
microservico_instagram_images/
├── app.py (novo - com suporte a áudio)
├── app_old.py (backup)
├── temp_files/ (criado automaticamente)
│   ├── *.jpg (imagens - 24h)
│   └── *.mp3 (áudios - 30 dias)
├── requirements.txt
└── Dockerfile
```

## 📦 Dependências

Adicione ao `requirements.txt`:

```txt
Flask==3.0.0
flask-cors==4.0.0
requests==2.31.0
```

Instale:
```bash
pip install -r requirements.txt
```

## 🐳 Docker

Se estiver usando Docker, o Dockerfile não precisa mudar:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

ENV PORT=5000
ENV BASE_URL=http://localhost:5000

EXPOSE 5000

CMD ["python", "app.py"]
```

Build e run:
```bash
docker build -t media-server .
docker run -p 5000:5000 -e BASE_URL=https://seu-dominio.com media-server
```

## 🧪 Testar

### 1. Health Check

```bash
curl https://seu-microservico.com/health
```

### 2. Upload de Áudio (teste local)

```bash
curl -X POST https://seu-microservico.com/upload/audio \
  -H "Content-Type: application/json" \
  -d '{
    "audio_url": "https://api.elevenlabs.io/v1/convai/conversations/conv_123/audio",
    "api_key": "sk_...",
    "conversation_id": "conv_123"
  }'
```

### 3. Acessar Áudio

```bash
curl https://seu-microservico.com/file/conv_123_abc12345.mp3 --output test.mp3
```

## 🔄 Limpeza Automática

O serviço limpa automaticamente:
- **Imagens**: Após 24 horas
- **Áudios**: Após 30 dias
- **Frequência**: A cada 60 minutos

Logs de limpeza:
```
🧹 Limpeza: 5 arquivos antigos removidos
```

## 📊 Monitoramento

Verifique estatísticas regularmente:

```bash
curl https://seu-microservico.com/stats
```

Se o `total_size_mb` estiver muito alto, considere:
- Reduzir `AUDIO_EXPIRY_DAYS`
- Aumentar `CLEANUP_INTERVAL_MINUTES`
- Adicionar mais espaço em disco

## ⚠️ Importante

1. **Backup**: Sempre faça backup antes de atualizar
2. **BASE_URL**: Configure corretamente para URLs públicas funcionarem
3. **Espaço em disco**: Áudios ocupam mais espaço que imagens
4. **Segurança**: Considere adicionar autenticação se necessário

## 🆘 Troubleshooting

### Erro: "Arquivo não encontrado"
- Verifique se o arquivo não expirou
- Confirme que o upload foi bem-sucedido

### Erro ao baixar áudio da API
- Verifique a API Key
- Confirme que o conversation_id está correto
- Aguarde alguns segundos após a ligação terminar

### Espaço em disco cheio
- Reduza `AUDIO_EXPIRY_DAYS`
- Execute limpeza manual: `DELETE /delete/{filename}`

## ✅ Checklist de Atualização

- [ ] Backup do `app.py` antigo
- [ ] Atualizar `requirements.txt`
- [ ] Instalar dependências: `pip install -r requirements.txt`
- [ ] Substituir `app.py`
- [ ] Configurar `BASE_URL`
- [ ] Reiniciar serviço
- [ ] Testar health check
- [ ] Testar upload de áudio
- [ ] Testar acesso ao áudio
- [ ] Verificar logs de limpeza

---

**Pronto! Seu microserviço agora suporta áudios! 🎉**
