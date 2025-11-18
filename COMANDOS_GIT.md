# 🚀 Comandos para Subir no GitHub

## 📋 Pré-requisitos

Certifique-se de estar na pasta do microserviço:
```bash
cd microservico_instagram_images
```

## 🔧 Comandos Git

### 1. Verificar status
```bash
git status
```

### 2. Adicionar arquivos modificados
```bash
git add app.py
git add requirements.txt
git add CHANGELOG.md
git add GUIA_ATUALIZACAO_AUDIO.md
git add app_backup_old.py
git add COMANDOS_GIT.md
```

Ou adicionar tudo de uma vez:
```bash
git add .
```

### 3. Commit com mensagem descritiva
```bash
git commit -m "feat: adiciona suporte a áudios no microserviço

- Novo endpoint /upload/audio para upload de áudios
- Suporte a upload via URL ou base64
- Áudios expiram em 30 dias (vs 24h para imagens)
- Endpoint /file/{filename} unificado para imagens e áudios
- Adicionada dependência requests
- Limpeza automática diferenciada por tipo de arquivo
- Health check e stats atualizados
- Backup da versão antiga em app_backup_old.py
- Documentação completa em GUIA_ATUALIZACAO_AUDIO.md"
```

### 4. Push para o GitHub
```bash
git push origin main
```

Ou se sua branch principal for `master`:
```bash
git push origin master
```

## 🏷️ (Opcional) Criar Tag de Versão

```bash
git tag -a v2.0.0 -m "Versão 2.0.0 - Suporte a áudios"
git push origin v2.0.0
```

## 🔍 Verificar no GitHub

Após o push, acesse:
```
https://github.com/seu-usuario/seu-repositorio
```

E verifique se os arquivos foram atualizados.

## 📝 Arquivos Modificados/Criados

- ✅ `app.py` - Versão nova com suporte a áudios
- ✅ `requirements.txt` - Adicionado requests
- ✅ `CHANGELOG.md` - Histórico de mudanças
- ✅ `GUIA_ATUALIZACAO_AUDIO.md` - Guia completo
- ✅ `app_backup_old.py` - Backup da versão antiga
- ✅ `COMANDOS_GIT.md` - Este arquivo

## 🐛 Troubleshooting

### Erro: "fatal: not a git repository"
```bash
# Inicializar repositório
git init
git remote add origin https://github.com/seu-usuario/seu-repositorio.git
```

### Erro: "rejected - non-fast-forward"
```bash
# Fazer pull primeiro
git pull origin main --rebase
git push origin main
```

### Erro: "Permission denied (publickey)"
```bash
# Verificar SSH key ou usar HTTPS
git remote set-url origin https://github.com/seu-usuario/seu-repositorio.git
```

## ✅ Checklist

- [ ] Verificar que está na pasta correta
- [ ] Executar `git status` para ver mudanças
- [ ] Adicionar arquivos com `git add`
- [ ] Fazer commit com mensagem descritiva
- [ ] Push para o GitHub
- [ ] Verificar no GitHub que os arquivos foram atualizados
- [ ] (Opcional) Criar tag de versão

---

**Pronto para subir! Execute os comandos acima na ordem.** 🚀
