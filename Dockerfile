FROM python:3.9-slim

WORKDIR /app

RUN pip install --upgrade pip

RUN apt-get update && apt-get install -y gcc python3-dev

COPY requirements.txt .

RUN apt-get update && apt-get install -y graphviz && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "-b", "0.0.0.0:10000", "app:app"]
