FROM python:3.8.18-slim

WORKDIR /ace

COPY . . 
RUN python3.8 -m pip install --upgrade pip && python3.8 -m pip install -r requirements.txt


EXPOSE 6878

ENTRYPOINT ./start-engine --client-console --live-cache-type memory --access-token apple --bind-all 

