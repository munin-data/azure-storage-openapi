FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8-alpine3.10

#RUN addgroup --system --gid 100 munindata && adduser --system --shell /bin/false --uid 1000 --gid munindata munindata
WORKDIR /app

COPY ./app /app

#RUN chown --recursive munindata:munindata /app
#USER munindata

