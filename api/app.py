# encoding: utf-8
import logging
import os
import subprocess
from logging.handlers import RotatingFileHandler
from flask_babelex import gettext, Babel
from flask import Flask, g, send_from_directory, jsonify, safe_join, request, flash, Response
from flask_mail import Mail
from flask_migrate import Migrate
from flask_security import Security
from flask_security import signals as FlaskSecuritySignals
from flask_cors import CORS, cross_origin
from flasgger import Swagger
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.utils import import_string
import commands
from utils.flake_id import FlakeId
from sqlalchemy import event
from sqlalchemy.engine import Engine
import time

from models import db, user_datastore
from utils.various import InvalidUsage, is_admin

from celery import Celery

from version import VERSION

__VERSION__ = VERSION

AVAILABLE_LOCALES = ["fr", "fr_FR", "en", "en_US", "pl"]

try:
    import sentry_sdk
    from sentry_sdk.integrations.flask import FlaskIntegration as SentryFlaskIntegration
    from sentry_sdk.integrations.celery import CeleryIntegration as SentryCeleryIntegration

    print(" * Sentry Flask/Celery support have been loaded")
    HAS_SENTRY = True
except ImportError:
    print(" * No Sentry Flask/Celery support available")
    HAS_SENTRY = False

GIT_VERSION = ""
gitpath = os.path.join(os.getcwd(), "../.git")
if os.path.isdir(gitpath):
    GIT_VERSION = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"])
    if GIT_VERSION:
        GIT_VERSION = GIT_VERSION.strip().decode("UTF-8")


def make_celery(remoulade):
    celery = Celery(remoulade.import_name, broker=remoulade.config["CELERY_BROKER_URL"])
    celery.conf.update(remoulade.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with remoulade.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery  # omnomnom


def create_app(config_filename="config.development.Config", app_name=None, register_blueprints=True):
    # App configuration
    app = Flask(app_name or __name__)
    app_settings = os.getenv("APP_SETTINGS", config_filename)
    print(f" * Loading config: '{app_settings}'")
    try:
        cfg = import_string(app_settings)()
    except ImportError:
        print(" *** Cannot import config ***")
        cfg = import_string("config.config.BaseConfig")
        print(" *** Default config loaded, expect problems ***")
    app.config.from_object(cfg)

    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    app.jinja_env.add_extension("jinja2.ext.with_")
    app.jinja_env.add_extension("jinja2.ext.do")
    app.jinja_env.globals.update(is_admin=is_admin)

    if HAS_SENTRY:
        sentry_sdk.init(
            app.config["SENTRY_DSN"],
            integrations=[SentryFlaskIntegration(), SentryCeleryIntegration()],
            release=f"{VERSION} ({GIT_VERSION})",
        )
        print(" * Sentry Flask/Celery support activated")
        print(" * Sentry DSN: %s" % app.config["SENTRY_DSN"])

    if app.debug:
        app.jinja_env.auto_reload = True
        logging.basicConfig(level=logging.DEBUG)

    # Logging
    if not app.debug:
        formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s " "[in %(pathname)s:%(lineno)d]")
        file_handler = RotatingFileHandler("%s/errors_app.log" % os.getcwd(), "a", 1000000, 1)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        app.logger.addHandler(file_handler)

    dbLogger = logging.getLogger("omnomnomnom.sqltime")
    dbLogger.setLevel(logging.DEBUG)

    CORS(app, origins=["*"])

    if app.debug:
        logging.getLogger("flask_cors.extension").level = logging.DEBUG

    mail = Mail(app)  # noqa: F841
    migrate = Migrate(app, db)  # noqa: F841 lgtm [py/unused-local-variable]
    babel = Babel(app)  # noqa: F841
    app.babel = babel

    template = {
        "swagger": "2.0",
        "info": {"title": "omnomnomnom API", "description": "API", "version": VERSION},
        "host": app.config["APP_HOST"],
        "basePath": "/",
        "schemes": ["https"],
        "securityDefinitions": {
        },
        "consumes": ["application/json"],
        "produces": ["application/json"],
    }

    db.init_app(app)

    # Setup Flask-Security
    security = Security(app, user_datastore)  # noqa: F841 lgtm [py/unused-local-variable]

    @FlaskSecuritySignals.password_reset.connect_via(app)
    @FlaskSecuritySignals.password_changed.connect_via(app)
    def log_password_reset(sender, user):
        if not user:
            return
        add_user_log(user.id, user.id, "user", "info", "Your password has been changed !")

    @FlaskSecuritySignals.reset_password_instructions_sent.connect_via(app)
    def log_reset_password_instr(sender, user, token):
        if not user:
            return
        add_user_log(user.id, user.id, "user", "info", "Password reset instructions sent.")

    @security.mail_context_processor
    def mail_ctx_proc():
        return dict()

    @babel.localeselector
    def get_locale():
        # if a user is logged in, use the locale from the user settings
        identity = getattr(g, "identity", None)
        if identity is not None and identity.id:
            return identity.user.locale
        # otherwise try to guess the language from the user accept
        # header the browser transmits.  We support fr/en in this
        # example.  The best match wins.
        return request.accept_languages.best_match(AVAILABLE_LOCALES)

    @babel.timezoneselector
    def get_timezone():
        identity = getattr(g, "identity", None)
        if identity is not None and identity.id:
            return identity.user.timezone


    @app.before_request
    def before_request():

        cfg = {
            "OMNOMNOMNOM_VERSION_VER": VERSION,
            "OMNOMNOMNOM_VERSION_GIT": GIT_VERSION,
        }
        if GIT_VERSION:
            cfg["OMNOMNOMNOM_VERSION"] = "{0}-{1}".format(VERSION, GIT_VERSION)
        else:
            cfg["OMNOMNOMNOM_VERSION"] = VERSION

        g.cfg = cfg

    @app.errorhandler(InvalidUsage)
    def handle_invalid_usage(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    @event.listens_for(Engine, "before_cursor_execute")
    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        if not False:
            return
        conn.info.setdefault("query_start_time", []).append(time.time())
        dbLogger.debug("Start Query: %s", statement)

    @event.listens_for(Engine, "after_cursor_execute")
    def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        if not False:
            return
        total = time.time() - conn.info["query_start_time"].pop(-1)
        dbLogger.debug("Query Complete!")
        dbLogger.debug("Total Time: %f", total)

    app.flake_id = FlakeId()

    if register_blueprints:
        # from controllers.api.v1.Xm import bp_X
        # app.register_blueprint(bp_X)

        swagger = Swagger(app, template=template)  # noqa: F841 lgtm [py/unused-local-variable]

    @app.route("/uploads/<string:thing>/<path:stuff>", methods=["GET"])
    @cross_origin(origins="*", methods=["GET", "HEAD", "OPTIONS"], expose_headers="content-length", send_wildcard=True)
    def get_uploads_stuff(thing, stuff):
        if app.testing or app.debug:
            directory = safe_join(app.config["UPLOADS_DEFAULT_DEST"], thing)
            app.logger.debug(f"serving {stuff} from {directory}")
            return send_from_directory(directory, stuff, as_attachment=True)
        else:
            app.logger.debug(f"X-Accel-Redirect serving {stuff}")
            resp = Response("")
            resp.headers["Content-Disposition"] = f"attachment; filename={stuff}"
            resp.headers["X-Accel-Redirect"] = f"/_protected/media/{thing}/{stuff}"
            resp.headers["Content-Type"] = ""  # empty it so Nginx will guess it correctly
            return resp

    @app.errorhandler(404)
    def page_not_found(msg):
        return jsonify({"error": "page not found"}), 404

    @app.errorhandler(403)
    def err_forbidden(msg):
        return jsonify({"error": "access forbidden"}), 403

    @app.errorhandler(410)
    def err_gone(msg):
        return jsonify({"error": "gone"}), 410

    if not app.debug:

        @app.errorhandler(500)
        def err_failed(msg):
            return jsonify({"error": "server error"}), 500

    @app.after_request
    def set_x_powered_by(response):
        response.headers["X-Powered-By"] = "omnomnomnom"
        return response

    # Register CLI commands
    app.cli.add_command(commands.db_datas)
    app.cli.add_command(commands.users)
    app.cli.add_command(commands.roles)
    app.cli.add_command(commands.system)

    return app
