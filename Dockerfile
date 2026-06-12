FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    libopus0 \
    libopus-dev \
    libffi-dev \
    libnacl-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install PyNaCl

COPY . .
CMD ["python", "main.py"]
