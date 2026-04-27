import os


class Settings:
    APP_NAME = os.getenv("APP_NAME", "Omni-Bookstore")
    COMMENT_API_URL = os.getenv(
        "COMMENT_API_URL",
        "http://10.255.255.1:65530/comments",
    )


settings = Settings()
