FROM python:3.8.18-slim

WORKDIR /ace

COPY requirements.txt .
RUN python3.8 -m pip install --upgrade pip && python3.8 -m pip install -r requirements.txt
COPY . .

EXPOSE 6878

ENTRYPOINT ./start-engine --client-console --live-cache-type memory --live-mem-cache-size 200000000  --bind-all --http-port 6878 --live-cache-size 200000000 --live-buffer 5 --access-token apple

