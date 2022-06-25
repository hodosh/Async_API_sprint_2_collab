from pydantic import BaseSettings, Field


class TestSettings(BaseSettings):
    es_host: str = Field('http://127.0.0.1:9204', env='ELASTIC_HOST')
    redis_host: str = Field('redis://127.0.0.1:6379', env='REDIS_HOST')
    api_host: str = Field('http://127.0.0.1:8000', env='API_HOST')


settings = TestSettings()
