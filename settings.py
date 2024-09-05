from typing import Optional

from pydantic import BaseSettings, Field, BaseModel, validator, AmqpDsn


class RabbitSettings(BaseModel):
    login: str
    password: str
    host: str
    port: str
    dsn: AmqpDsn = Field(None)

    @validator("dsn", always=True)
    def build_dsn(cls, value, values):
        return AmqpDsn.build(
            scheme="amqp",
            user=values["login"],
            password=values["password"],
            port=values["port"],
            host=values["host"],
        )


class Settings(BaseSettings):
    rabbit_settings: RabbitSettings

    class Config:
        env_nested_delimiter = "__"


settings = Settings()
print(settings.rabbit_settings.dsn)
