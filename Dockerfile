FROM python:3.11-slim

WORKDIR /app

# Copiar requirements
COPY requirements.txt .

# Instalar dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY app.py .

# Criar pasta para arquivos temporários (imagens e áudios)
RUN mkdir -p temp_files

# Expor porta
EXPOSE 5000

# Variáveis de ambiente (configurar no Easypanel)
ENV BASE_URL=http://localhost:5000
ENV PORT=5000
ENV IMAGE_EXPIRY_HOURS=24
ENV AUDIO_EXPIRY_DAYS=30
ENV CLEANUP_INTERVAL_MINUTES=60

# Rodar com gunicorn (produção)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "app:app"]
