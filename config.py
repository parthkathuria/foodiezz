from pydantic import Field
from pydantic.env_settings import BaseSettings


class AppConfig(BaseSettings):
    socrata_domain: str = Field(default="data.sfgov.org", env="SOCRATA_DOMAIN")
    socrata_dataset_id: str = Field(default="jjew-r69b", env="SOCRATA_DATASET_ID")
    app_token: str = Field(default=None, env="APP_TOKEN")
    query_limit: int = Field(default=10, env="QUERY_LIMIT")

    class Config:
        env_file = "config.env"
