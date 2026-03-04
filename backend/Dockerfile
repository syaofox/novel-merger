FROM python:3.11-slim-bookworm AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    fonts-wqy-microhei \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -L -o /tmp/pandoc.tar.gz https://github.com/jgm/pandoc/releases/download/3.1.13/pandoc-3.1.13-linux-amd64.tar.gz \
    && tar -xzf /tmp/pandoc.tar.gz -C /tmp \
    && cp -rf /tmp/pandoc-3.1.13/* /usr/local/ \
    && rm -rf /tmp/pandoc*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.11-slim-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
    fonts-wqy-microhei \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -u 1000 appuser

RUN curl -L -o /tmp/pandoc.tar.gz https://github.com/jgm/pandoc/releases/download/3.1.13/pandoc-3.1.13-linux-amd64.tar.gz \
    && tar -xzf /tmp/pandoc.tar.gz -C /tmp \
    && cp -rf /tmp/pandoc-3.1.13/* /usr/local/ \
    && rm -rf /tmp/pandoc*

WORKDIR /app

COPY --from=builder /root/.local /home/appuser/.local
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /usr/local/share /usr/local/share
ENV PATH=/usr/local/bin:/home/appuser/.local/bin:$PATH
USER appuser

COPY --chown=appuser:appuser . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
