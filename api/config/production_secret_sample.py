from .development import Config as BaseConfig


class Config(BaseConfig):
    # See the Configuration documentation at:
    # FIXME AHAH
    # For all the config keys you can use

    # Please generate me with: openssl rand -hex 42
    SECRET_KEY = "fdsfsdfsdfsdfdsfsdfsdfsdfdsfsdfsd"
    # Please generate me with: openssl rand -hex 5
    SECURITY_PASSWORD_SALT = "omgponies"
    # Set your DB URI
    SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://dashie@localhost/omnomnomnom"

    APP_HOST = "miam.host.tld"

    # If you are using Sentry, otherwise, set to None
    SENTRY_DSN = None

    # If you are using a modified instance, please set your own repository URL
    SOURCES_REPOSITORY_URL = "https://github.com/dashie/omnomnomnom"

    # Email settings
    MAIL_SERVER = "localhost"
    # MAIL_PORT = 25
    # MAIL_USE_TLS = False
    # MAIL_USE_SSL = False
    # MAIL_USERNAME = None
    # MAIL_PASSWORD = None

    # CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'
    # CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'
