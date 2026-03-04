FROM python:3.11-slim-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
    fonts-wqy-microhei \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -L -o /tmp/pandoc.tar.gz https://github.com/jgm/pandoc/releases/download/3.1.13/pandoc-3.1.13-linux-amd64.tar.gz \
    && tar -xzf /tmp/pandoc.tar.gz -C /tmp \
    && cp -rf /tmp/pandoc-3.1.13/* /usr/local/ \
    && rm -rf /tmp/pandoc*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
