FROM eclipse-temurin:17-jre-jammy AS java_runtime

FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PRO_ENGLISH_AI_STORAGE_MODE=session \
    JAVA_HOME=/opt/java/openjdk \
    JAVA_TOOL_OPTIONS="-Xms64m -Xmx256m" \
    PATH="/opt/java/openjdk/bin:${PATH}"

WORKDIR /app

COPY --from=java_runtime /opt/java/openjdk /opt/java/openjdk

COPY requirements.txt .
RUN python -m pip install --upgrade pip \
    && python -m pip install -r requirements.txt

COPY scripts/install_languagetool.py /tmp/install_languagetool.py
RUN python /tmp/install_languagetool.py \
    && rm /tmp/install_languagetool.py

COPY . .

EXPOSE 8501

CMD streamlit run app.py \
    --server.address=0.0.0.0 \
    --server.port=${PORT:-8501} \
    --server.headless=true \
    --browser.gatherUsageStats=false
