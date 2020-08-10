import os

#                                 .i;;;;i.
#                               iYcviii;vXY:
#                             .YXi       .i1c.
#                            .YC.     .    in7.
#                           .vc.   ......   ;1c.
#                           i7,   ..        .;1;
#                          i7,   .. ...      .Y1i
#                         ,7v     .6MMM@;     .YX,
#                        .7;.   ..IMMMMMM1     :t7.
#                       .;Y.     ;$MMMMMM9.     :tc.
#                       vY.   .. .nMMM@MMU.      ;1v.
#                      i7i   ...  .#MM@M@C. .....:71i
#                     it:   ....   $MMM@9;.,i;;;i,;tti
#                    :t7.  .....   0MMMWv.,iii:::,,;St.
#                   .nC.   .....   IMMMQ..,::::::,.,czX.
#                  .ct:   ....... .ZMMMI..,:::::::,,:76Y.
#                  c2:   ......,i..Y$M@t..:::::::,,..inZY
#                 vov   ......:ii..c$MBc..,,,,,,,,,,..iI9i
#                i9Y   ......iii:..7@MA,..,,,,,,,,,....;AA:
#               iIS.  ......:ii::..;@MI....,............;Ez.
#              .I9.  ......:i::::...8M1..................C0z.
#             .z9;  ......:i::::,.. .i:...................zWX.
#             vbv  ......,i::::,,.      ................. :AQY
#            c6Y.  .,...,::::,,..:t0@@QY. ................ :8bi
#           :6S. ..,,...,:::,,,..EMMMMMMI. ............... .;bZ,
#          :6o,  .,,,,..:::,,,..i#MMMMMM#v.................  YW2.
#         .n8i ..,,,,,,,::,,,,.. tMMMMM@C:.................. .1Wn
#         7Uc. .:::,,,,,::,,,,..   i1t;,..................... .UEi
#         7C...::::::::::::,,,,..        ....................  vSi.
#         ;1;...,,::::::,.........       ..................    Yz:
#          v97,.........                                     .voC.
#           izAotX7777777777777777777777777777777777777777Y7n92:
#             .;CoIIIIIUAA666666699999ZZZZZZZZZZZZZZZZZZZZ6ov.
#
#                          !!! ATTENTION !!!
# DO NOT EDIT THIS FILE! THIS FILE CONTAINS THE DEFAULT VALUES FOR THE CON-
# FIGURATION! EDIT YOUR OWN CONFIG FILE (based on production.py or development.py or testing.py).
# AND DICTATE THE APP TO USE YOUR FILE WITH ENV VARIABLE:
# APP_SETTINGS='config.yourEnv.Config'
#
# Editing this file is done at your own risks, don't cry if doing that transforms your cat in an opossum.


def bool_env(var_name, default=False):
    test_val = os.getenv(var_name, default)
    if test_val in ("False", "false", "0", "no"):
        return False
    return bool(test_val)


class BaseConfig(object):
    """ Base configuration, pls dont edit me """

    # Debug and testing specific
    TESTING = bool_env("TESTING", False)
    DEBUG = bool_env("DEBUG", False)

    @property
    def TEMPLATES_AUTO_RELOAD(self):
        return self.DEBUG

    # Can users register
    REGISTRATION_ENABLED = bool_env("REGISTRATION_ENABLED", False)

    # Registration, same as upper
    @property
    def SECURITY_REGISTERABLE(self):
        return self.REGISTRATION_ENABLED

    # Secret key, you are supposed to generate one
    # Ex: `openssl rand -hex 42`
    SECRET_KEY = os.getenv("SECRET_KEY", None)
    # Ex: `openssl rand -hex 5`
    SECURITY_PASSWORD_SALT = os.getenv("SECURITY_PASSWORD_SALT", None)

    # Database stuff
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI", "postgresql+psycopg2://postgres@localhost/omnomnomnom")
    SQLALCHEMY_ECHO = bool_env("SQLALCHEMY_ECHO", False)
    # Thoses two shouldn't be touched
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True

    # Flask-Security stuff
    # Should users confirm theire email address ?
    SECURITY_CONFIRMABLE = bool_env("SECURITY_CONFIRMABLE", True)

    # We have an alternative way
    SECURITY_RECOVERABLE = False
    # Don't change or you will break things
    SECURITY_CHANGEABLE = True
    # Same or I bite you
    SECURITY_PASSWORD_HASH = "bcrypt"
    SECURITY_SEND_REGISTER_EMAIL = True
    SECURITY_SEND_PASSWORD_CHANGE_EMAIL = True
    SECURITY_SEND_PASSWORD_RESET_NOTICE_EMAIL = True
    SECURITY_FLASH_MESSAGES = False
    SECURITY_URL_PREFIX = '/api/auth'

    SECURITY_POST_CONFIRM_VIEW = "/auth/confirmed"
    SECURITY_CONFIRM_ERROR_VIEW = "/auth/confirm-error"
    SECURITY_RESET_VIEW = "/auth/reset-password"
    SECURITY_RESET_ERROR_VIEW = "/auth/reset-password"
    SECURITY_REDIRECT_BEHAVIOR = "spa"

    # enforce CSRF protection for session / browser - but allow token-based
    # API calls to go through
    SECURITY_CSRF_PROTECT_MECHANISMS = ["session", "basic"]
    SECURITY_CSRF_IGNORE_UNAUTH_ENDPOINTS = True

    SECURITY_CSRF_COOKIE = {"key": "XSRF-TOKEN"}
    WTF_CSRF_CHECK_DEFAULT = False
    WTF_CSRF_TIME_LIMIT = None

    # Backend default language
    BABEL_DEFAULT_LOCALE = os.getenv("BABEL_DEFAULT_LOCALE", "en")
    # Not sure this one has any effect...
    BABEL_DEFAULT_TIMEZONE = os.getenv("BABEL_DEFAULT_TIMEZONE", "UTC")

    # If using sentry
    SENTRY_DSN = os.getenv("SENTRY_DSN", None)

    # Broker setup for Celery, same redis base for both
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://127.0.0.1:6379/0")
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://127.0.0.1:6379/0")

    # ActivityPub stuff
    AP_ENABLED = bool_env("AP_ENABLED", False)

    # Sources of that instance, should be your repos if forked
    SOURCES_REPOSITORY_URL = os.getenv("SOURCES_REPOSITORY_URL", "https://github.com/dashie/omnopmnomnom")

    # Mail setup
    MAIL_SERVER = os.getenv("MAIL_SERVER", "localhost")
    MAIL_PORT = os.getenv("MAIL_PORT", 25)
    MAIL_USE_TLS = bool_env("MAIL_USE_TLS", False)
    MAIL_USE_SSL = bool_env("MAIL_USE_SSL", False)
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", None)
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", None)

    SERVER_NAME = "localhost"

    @property
    def MAIL_DEFAULT_SENDER(self):
        return os.getenv("MAIL_DEFAULT_SENDER", f"postmaster@{self.SERVER_NAME}")

    @property
    def SECURITY_EMAIL_SENDER(self):
        return os.getenv("MAIL_DEFAULT_SENDER", f"postmaster@{self.SERVER_NAME}")

    SECURITY_EMAIL_SUBJECT_REGISTER = os.getenv("SECURITY_EMAIL_SUBJECT_REGISTER", "Welcome to omnomnomnom")

    # Don't touch
    SWAGGER_UI_DOC_EXPANSION = "list"

    SECURITY_CLI_USERS_NAME = False
    SECURITY_CLI_ROLES_NAME = False
