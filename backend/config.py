from pydantic_settings import BaseSettings

class Config(BaseSettings):
    postgres_host: str = "localhost"
    postgres_password: str = "test"
    postgres_user: str = "test"
    postgres_database: str = "test"
    postgres_port: str = "5432"

    actual_base_url: str = "http://localhost:5007"
    actual_api_key: str | None = None

    actual_unknown_payee: str | None = None
    actual_fee_category: str = "ff41dcbd-5962-4b32-b3fe-ce9d63cf9c25"
    # dynamic categories: ACTUAL_CAT_<TELLER_CATEGORY>

    mqtt_host: str | None = None
    mqtt_user: str | None = None
    mqtt_passwd: str | None = None

    pushover_token: str | None = None
    pushover_user: str | None = None

    exchangeratesio_access_key: str | None = None

config = Config()