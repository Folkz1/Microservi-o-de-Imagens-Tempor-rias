# 📝 Changelog - Media Server

## [2.0.0] - 2025-11-18

### ✨ Novidades
- **Suporte a áudios**: Agora o microserviço suporta upload e armazenamento de áudios MP3
- **Upload via URL**: Possibilidade de fazer upload passando URL da API (ex: ElevenLabs)
- **Expiração diferenciada**: Imagens expiram em 24h, áudios em 30 dias
- **Pasta unificada**: Todos os arquivos agora vão para `temp_files/`

### 🔄 Mudanças
- Endpoint `/image/{filename}` → `/file/{filename}` (retrocompatível)
- Endpoint `/upload` → `/upload/image` (retrocompatível)
- Novo endpoint `/upload/audio`
- Health check agora mostra imagens e áudios separadamente
- Stats agora mostra estatísticas de ambos os tipos

### 🐛 Correções
- Limpeza automática agora diferencia tipos de arquivo
- Melhor tratamento de erros no download de URLs

### 📦 Dependências
- Adicionado: `requests==2.31.0`

### 🔧 Migração da v1.0

1. Backup do `app.py` antigo (já feito automaticamente como `app_backup_old.py`)
2. Atualizar `requirements.txt`
3. Instalar nova dependência: `pip install requests==2.31.0`
4. Reiniciar serviço

**Nota**: A pasta `temp_images/` antiga pode ser mantida ou removida. O novo serviço usa `temp_files/`.

---

## [1.0.0] - 2024-11-XX

### ✨ Lançamento Inicial
- Upload de imagens via base64
- Expiração automática em 24h
- Limpeza automática
- Health check e estatísticas
- Integração com Instagram API

