# 🚀 QUICKSTART - Deploy em 5 Minutos

## ✅ Validação Completa

- ✅ Código Python sem erros
- ✅ Dockerfile otimizado
- ✅ Requirements.txt correto
- ✅ Testes incluídos
- ✅ Documentação completa
- ✅ **Código no GitHub**: https://github.com/Folkz1/Microservi-o-de-Imagens-Tempor-rias

---

## 📦 O que foi criado

```
microservico_instagram_images/
├── app.py                    # Servidor Flask principal
├── Dockerfile                # Container Docker otimizado
├── requirements.txt          # Dependências Python
├── .dockerignore            # Arquivos ignorados no build
├── .gitignore               # Arquivos ignorados no Git
├── .env.example             # Template de variáveis
├── README.md                # Documentação completa
├── DEPLOY_EASYPANEL.md      # Guia de deploy detalhado
├── test_local.py            # Script de testes
└── temp_images/             # Pasta para imagens temporárias
    └── .gitkeep
```

---

## 🎯 Deploy no Easypanel (5 minutos)

### 1️⃣ Criar Serviço

1. Acessar Easypanel
2. Clicar em **"Create Service"**
3. Escolher **"App from GitHub"**
4. Conectar repositório: `Folkz1/Microservi-o-de-Imagens-Tempor-rias`
5. Branch: `main`
6. Build method: **Dockerfile**

### 2️⃣ Configurar Variáveis

Adicionar em **Environment Variables**:

```env
BASE_URL=https://instagram-images.SEU-DOMINIO.easypanel.host
PORT=5000
```

**⚠️ IMPORTANTE:** Depois que o serviço subir, voltar e atualizar `BASE_URL` com a URL real!

### 3️⃣ Configurar Domínio

1. Ir em **Domains**
2. Adicionar: `instagram-images` (ou nome que preferir)
3. Anotar a URL final, exemplo:
   ```
   https://instagram-images.7exngm.easypanel.host
   ```

### 4️⃣ Atualizar BASE_URL

1. Voltar em **Environment Variables**
2. Atualizar `BASE_URL` com a URL real do passo 3
3. Reiniciar serviço

### 5️⃣ Testar

```bash
# Health check
curl https://instagram-images.SEU-DOMINIO.easypanel.host/health

# Deve retornar:
{
  "status": "healthy",
  "service": "instagram-image-server",
  "images_stored": 0,
  "expiry_hours": 24
}
```

---

## 🧪 Teste Completo

```bash
# Upload de imagem de teste
curl -X POST https://instagram-images.SEU-DOMINIO.easypanel.host/upload \
  -H "Content-Type: application/json" \
  -d '{"image_base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="}'

# Resposta esperada:
{
  "success": true,
  "image_url": "https://instagram-images.SEU-DOMINIO.easypanel.host/image/abc123.jpg",
  "filename": "abc123.jpg",
  "size_bytes": 68,
  "expires_at": "2024-11-19T10:00:00Z"
}

# Acessar a imagem no navegador:
# https://instagram-images.SEU-DOMINIO.easypanel.host/image/abc123.jpg
```

---

## 🔗 Usar no N8N

### No workflow `instagram_auto_post.json`:

**Node: HTTP Request - Upload Imagem**

```javascript
// URL
https://instagram-images.SEU-DOMINIO.easypanel.host/upload

// Method
POST

// Body (JSON)
{
  "image_base64": "={{ $json.image_base64 }}"
}

// Response
// Extrair: $json.image_url
```

---

## 📊 Endpoints Disponíveis

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/health` | GET | Health check |
| `/upload` | POST | Upload base64 → URL |
| `/image/{filename}` | GET | Servir imagem |
| `/stats` | GET | Estatísticas |
| `/delete/{filename}` | DELETE | Deletar imagem |

---

## ⚙️ Configurações Padrão

- **Expiração de imagens**: 24 horas
- **Limpeza automática**: A cada 60 minutos
- **Workers Gunicorn**: 2
- **Timeout**: 120 segundos
- **CORS**: Habilitado

---

## 🐛 Troubleshooting

### Serviço não inicia
- Verificar logs no Easypanel
- Confirmar que Dockerfile está na raiz
- Verificar se requirements.txt está correto

### Imagem não aparece
- Verificar se `BASE_URL` está correto
- Confirmar que imagem não expirou (24h)
- Testar URL diretamente no navegador

### Erro 404 ao acessar imagem
- Imagem pode ter expirado
- Verificar se filename está correto
- Checar logs do servidor

---

## 📈 Monitoramento

```bash
# Ver estatísticas
curl https://instagram-images.SEU-DOMINIO.easypanel.host/stats

# Resposta:
{
  "total_images": 42,
  "total_size_mb": 125.5,
  "expiry_hours": 24,
  "cleanup_interval_minutes": 60
}
```

---

## 🎯 Próximos Passos

1. ✅ Deploy no Easypanel
2. ✅ Testar endpoints
3. ✅ Anotar URL final
4. ⏭️ Configurar no workflow N8N de postagem
5. ⏭️ Testar fluxo completo de postagem

---

## 📚 Documentação Completa

- **README.md** - Documentação técnica completa
- **DEPLOY_EASYPANEL.md** - Guia detalhado de deploy
- **test_local.py** - Script para testes locais

---

## ✅ Checklist de Validação

- [x] Código Python sem erros de sintaxe
- [x] Dockerfile otimizado para produção
- [x] Requirements.txt com versões fixas
- [x] .dockerignore configurado
- [x] .gitignore configurado
- [x] Documentação completa
- [x] Testes incluídos
- [x] **Código no GitHub**
- [ ] Deploy no Easypanel
- [ ] Testes em produção
- [ ] Integração com N8N

---

## 🔗 Links Úteis

- **GitHub**: https://github.com/Folkz1/Microservi-o-de-Imagens-Tempor-rias
- **Easypanel**: https://easypanel.io
- **Flask Docs**: https://flask.palletsprojects.com
- **Instagram API**: https://developers.facebook.com/docs/instagram-api

---

## 💡 Dicas

1. **Sempre** atualizar `BASE_URL` após deploy
2. **Monitorar** uso de disco com `/stats`
3. **Configurar** volume persistente se necessário
4. **Adicionar** autenticação para produção (opcional)
5. **Testar** localmente antes de deploy

---

**🎉 Tudo validado e pronto para deploy!**
