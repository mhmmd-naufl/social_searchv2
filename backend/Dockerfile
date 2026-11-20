FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    CHROMEDRIVER_PATH=/usr/bin/chromedriver \
    BROWSER_BINARY=/usr/bin/chromium \
    HEADLESS=1

RUN apt-get update \
 && apt-get install -y --no-install-recommends chromium chromium-driver \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
 && python -c "import nltk; nltk.download('stopwords', quiet=True)"

COPY app/ ./app/

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
