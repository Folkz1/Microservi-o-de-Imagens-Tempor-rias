FROM python:3.11-slim

WORKDIR /app

# Copiar requirements
COPY requirements.txt .

# Instalar dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY app.py .

# Criar pasta para imagens temporárias
RUN mkdir -p temp_images

# Expor porta
EXPOSE 5000

# Variável de ambiente para URL base (configurar no Easypanel)
ENV BASE_URL=http://localhost:5000
ENV PORT=5000

# Rodar com gunicorn (produção)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "app:app"]
