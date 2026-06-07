FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PRO_ENGLISH_AI_STORAGE_MODE=session \
    JAVA_TOOL_OPTIONS="-Xms64m -Xmx256m"

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        openjdk-17-jre-headless \
        unzip \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

RUN mkdir -p /app/.runtime \
    && curl --fail --location --retry 3 \
        https://languagetool.org/download/LanguageTool-6.5.zip \
        --output /tmp/languagetool.zip \
    && unzip -q /tmp/languagetool.zip -d /app/.runtime \
    && rm /tmp/languagetool.zip

COPY . .

EXPOSE 8501

CMD streamlit run app.py \
    --server.address=0.0.0.0 \
    --server.port=${PORT:-8501} \
    --server.headless=true \
    --browser.gatherUsageStats=false
