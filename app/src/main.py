import aioredis
import uvicorn
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from api.v1 import films, persons, genres
from core import config
from db import elastic, redis

app = FastAPI(
    title=config.PROJECT_NAME,
    docs_url='/api/v1/openapi',
    openapi_url='/api/v1/openapi.json',
    default_response_class=ORJSONResponse,
)


@app.on_event('startup')
async def startup():
    redis.redis = await aioredis.create_redis_pool((config.REDIS_HOST, config.REDIS_PORT), minsize=10, maxsize=20)
    elastic.es = AsyncElasticsearch(hosts=[f'{config.ES_HOST}:{config.ES_PORT}'])


@app.on_event('shutdown')
async def shutdown():
    await redis.redis.close()
    await elastic.es.close()


@app.middleware('http')
async def before_request(request: Request, call_next):
    request_id = request.headers.get('X-Request-Id')
    if not request_id:
        raise RuntimeError('request id is required')
    return await call_next(request)


# Подключаем роутер к серверу, указав префикс /v1/films
# Теги указываем для удобства навигации по документации
app.include_router(films.router, prefix='/api/v1/films', tags=['Film'])
app.include_router(persons.router, prefix='/api/v1/persons', tags=['Person'])
app.include_router(genres.router, prefix='/api/v1/genres', tags=['Genre'])

# добавляем трассировку
trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(
        JaegerExporter(
            agent_host_name=config.JAEGER_HOST,
            agent_port=config.JAEGER_PORT,
        )
    )
)
# Чтобы видеть трейсы в консоли
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
FastAPIInstrumentor().instrument_app(app)

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8000,
    )
