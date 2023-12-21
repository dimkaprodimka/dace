FROM python:3.8.18-slim

ENV HTTP_PORT 8080

WORKDIR /ace

COPY . . 
RUN python3.8 -m pip install --upgrade pip && python3.8 -m pip install -r requirements.txt


EXPOSE $HTTP_PORT

ENTRYPOINT ./start-engine --client-console --live-cache-type memory --live-mem-cache-size 262144000  --access-token apple --bind-all --http-port $HTTP_PORT 

