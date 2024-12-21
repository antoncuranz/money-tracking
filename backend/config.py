import os


class Config:
    postgres_host = os.getenv("POSTGRES_HOST")
    postgres_password = os.getenv("POSTGRES_PASSWORD")
    postgres_user = os.getenv("POSTGRES_USER")
    postgres_database = os.getenv("POSTGRES_DATABASE")
    postgres_port = os.getenv("POSTGRES_PORT", "5432")

    actual_base_url = os.getenv("ACTUAL_BASE_URL", "http://localhost:5007")
    actual_api_key = os.getenv("ACTUAL_API_KEY")

    actual_unknown_payee = os.getenv("ACTUAL_UNKNOWN_PAYEE")
    actual_fee_category = os.getenv("ACTUAL_CAT_FX_FEES", "ff41dcbd-5962-4b32-b3fe-ce9d63cf9c25")
    # dynamic categories: ACTUAL_CAT_<TELLER_CATEGORY>

    mqtt_host = os.getenv("MQTT_HOST")
    mqtt_user = os.getenv("MQTT_USER")
    mqtt_passwd = os.getenv("MQTT_PASSWD")

    exchangeratesio_access_key = os.getenv("EXCHANGERATESIO_ACCESS_KEY")
