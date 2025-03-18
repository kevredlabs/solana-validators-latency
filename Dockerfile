FROM python:3.9-slim
RUN apt-get update && apt-get install -y --no-install-recommends nmap iputils-ping netcat-openbsd net-tools && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY main.py .
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "main.py"] 
