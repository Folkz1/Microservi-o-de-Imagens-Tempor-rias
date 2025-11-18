# 🚀 Deploy no Easypanel - Guia Rápido

## Passo 1: Criar Repositório Git (Opcional)

Se quiser versionar:
```bash
cd microservico_instagram_images
git init
git add .
git commit -m "Initial commit: Instagram Image Server"
```

## Passo 2: Deploy no Easypanel

### Opção A: Deploy via Git (Recomendado)

1. **Push para GitHub/GitLab**
   ```bash
   git remote add origin https://github.com/seu-usuario/instagram-image-server.git
   git push -u origin main
   ```

2. **No Easypanel:**
   - Criar novo serviço
   - Tipo: **App (GitHub)**
   - Conectar repositório
   - Branch: `main`
   - Build: **Dockerfile**

### Opção B: Deploy Manual (Mais Rápido)

1. **No Easypanel:**
   - Criar novo serviço
   - Tipo: **App (Docker)**
   - Nome: `instagram-image-server`

2. **Fazer upload dos arquivos:**
   - `app.py`
   - `requirements.txt`
   - `Dockerfile`
   - `.dockerignore`

## Passo 3: Configurar Variáveis de Ambiente

No painel do Easypanel, adicionar:

```env
BASE_URL=https://instagram-images.SEU-DOMINIO.easypanel.host
PORT=5000
```

**⚠️ IMPORTANTE:** Substituir `SEU-DOMINIO` pelo domínio real que o Easypanel fornecer!

## Passo 4: Configurar Domínio

1. No Easypanel, ir em **Domains**
2. Adicionar domínio:
   - Subdomínio: `instagram-images`
   - Ou usar o domínio padrão: `*.easypanel.host`

3. **Anotar a URL final**, exemplo:
   ```
   https://instagram-images.7exngm.easypanel.host
   ```

## Passo 5: Testar Deploy

```bash
# Health check
curl https://instagram-images.SEU-DOMINIO.easypanel.host/health

# Upload de teste
curl -X POST https://instagram-images.SEU-DOMINIO.easypanel.host/upload \
  -H "Content-Type: application/json" \
  -d '{"image_base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="}'

# Stats
curl https://instagram-images.SEU-DOMINIO.easypanel.host/stats
```

## Passo 6: Configurar Volume (Opcional)

Para persistir imagens entre restarts:

1. No Easypanel, ir em **Volumes**
2. Adicionar volume:
   - Mount path: `/app/temp_images`
   - Size: `5GB` (ajustar conforme necessário)

## Passo 7: Configurar no N8N

Usar a URL final nos workflows:

```javascript
// No workflow de postagem do Instagram
const uploadUrl = "https://instagram-images.SEU-DOMINIO.easypanel.host/upload";
```

## 🔧 Troubleshooting

### Erro: "Application failed to start"

**Verificar logs no Easypanel:**
- Ir em **Logs**
- Procurar por erros de Python/Flask

**Soluções comuns:**
- Verificar se `requirements.txt` está correto
- Verificar se `Dockerfile` está na raiz
- Verificar se porta 5000 está exposta

### Erro: "Cannot connect to service"

**Verificar:**
- Domínio está configurado corretamente
- Serviço está rodando (status green)
- Firewall/proxy não está bloqueando

### Imagens não aparecem

**Verificar:**
- `BASE_URL` está correto nas variáveis de ambiente
- URL retornada no upload está acessível
- Imagem não expirou (24h)

## 📊 Monitoramento

### Verificar saúde do serviço:
```bash
watch -n 30 'curl -s https://instagram-images.SEU-DOMINIO.easypanel.host/health | jq'
```

### Verificar uso de disco:
```bash
curl https://instagram-images.SEU-DOMINIO.easypanel.host/stats
```

## 🔒 Segurança (Opcional)

### Adicionar autenticação básica:

Editar `app.py`:

```python
from functools import wraps
from flask import request

API_KEY = os.getenv("API_KEY", "seu-token-secreto")

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.headers.get('X-API-Key') != API_KEY:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route("/upload", methods=["POST"])
@require_api_key
def upload_image():
    # ... código existente
```

Adicionar variável de ambiente:
```env
API_KEY=seu-token-super-secreto-aqui
```

Usar no N8N:
```javascript
// Headers do HTTP Request
{
  "X-API-Key": "seu-token-super-secreto-aqui"
}
```

## ✅ Checklist Final

- [ ] Serviço rodando no Easypanel
- [ ] Domínio configurado
- [ ] `BASE_URL` correto nas variáveis
- [ ] Health check retorna 200
- [ ] Upload de teste funciona
- [ ] Imagem acessível via URL
- [ ] Stats mostrando dados corretos
- [ ] URL anotada para usar no N8N

## 🎯 Próximo Passo

Agora você pode usar este serviço no workflow de postagem do Instagram!

**URL para usar no N8N:**
```
https://instagram-images.SEU-DOMINIO.easypanel.host/upload
```
