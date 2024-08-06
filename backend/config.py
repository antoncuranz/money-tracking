import os


class Config:
    database_path = os.getenv("DB_PATH", "sqlite.db")

    teller_cert = ("./teller/certificate.pem", "./teller/private_key.pem")

    actual_api_key = os.getenv("ACTUAL_API_KEY")
    actual_sync_id = os.getenv("ACTUAL_SYNC_ID")

    actual_fee_category = os.getenv("ACTUAL_CAT_FEES", "ff41dcbd-5962-4b32-b3fe-ce9d63cf9c25")
    actual_other_category = os.getenv("ACTUAL_CAT_OTHER", "7e179c86-50cd-4f9e-86dd-d085dfa21a10")

    ibkr_host = os.getenv("IBKR_HOST", "localhost")
    ibkr_port = os.getenv("IBKR_PORT", "5000")

    exchangeratesio_access_key = os.getenv("EXCHANGERATESIO_ACCESS_KEY")
