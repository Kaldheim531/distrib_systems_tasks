FROM python:3.11-slim AS builder

WORKDIR /build

COPY requirements.txt .
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

FROM python:3.11-slim AS runtime

WORKDIR /app

COPY --from=builder /install /usr/local
COPY app ./app

EXPOSE 8156

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8156"]
