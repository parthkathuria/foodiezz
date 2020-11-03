from pydantic import Field
from pydantic.env_settings import BaseSettings

from constants import DEFAULT_SOCRATA_DOMAIN, DEFAULT_SOCRATA_DATASET_ID, DEFAULT_PAGE_LIMIT


class AppConfig(BaseSettings):
    """
    The config class that reads the Environment variables and the .env files which are defined based on the
    environment in which you are running your app.
    """
    socrata_domain: str = Field(default=DEFAULT_SOCRATA_DOMAIN, env="SOCRATA_DOMAIN")
    socrata_dataset_id: str = Field(default=DEFAULT_SOCRATA_DATASET_ID, env="SOCRATA_DATASET_ID")
    app_token: str = Field(default=None, env="APP_TOKEN")
    page_limit: int = Field(default=DEFAULT_PAGE_LIMIT, env="PAGE_LIMIT")

    class Config:
        """
        Subclass allows you to define meta data like the default path of the config file.
        """
        env_file = "./env/config.env"
