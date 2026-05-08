from dotenv import load_dotenv
import os

load_dotenv()


class Settings:
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        self.secret_key = os.getenv("SECRET_KEY")
        self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
        self.debug = os.getenv("DEBUG", "False").lower() == "true"

settings = Settings()

