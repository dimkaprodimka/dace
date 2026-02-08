FROM python:3.8.18-slim

ENV HTTP_PORT 6878

WORKDIR /ace

COPY requirements.txt .
RUN python3.8 -m pip install --upgrade pip && python3.8 -m pip install -r requirements.txt
COPY . .

EXPOSE $HTTP_PORT

ENTRYPOINT ./start-engine --client-console --live-cache-type memory --live-mem-cache-size 100000000  --bind-all --http-port $HTTP_PORT --live-cache-size 100000000 --max-peers 20 --access-token apple

