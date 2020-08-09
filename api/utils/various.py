import datetime
import hashlib
from os.path import splitext
import random
import string

from flask_security import current_user

from models import db, Role, Logging


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        rv["status"] = "error"
        rv["code"] = self.status_code
        return rv


def is_admin():
    adm = Role.query.filter(Role.name == "admin").first()
    if not current_user or not current_user.is_authenticated or not adm:
        return False
    if adm in current_user.roles:
        return True
    return False


def add_log(category, level, message):
    if not category or not level or not message:
        print("!! Fatal error in add_log() one of three variables not set")
    print("[LOG][{0}][{1}] {2}".format(level.upper(), category, message))
    a = Logging(category=category, level=level.upper(), message=message)
    db.session.add(a)
    db.session.commit()


def duration_human(seconds):
    if seconds is None:
        return "error"
    seconds = float(seconds)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    years, days = divmod(days, 365.242199)

    minutes = int(minutes)
    hours = int(hours)
    days = int(days)
    years = int(years)

    if years > 0:
        return "%d year" % years + "s" * (years != 1)
    elif days > 0:
        return "%d day" % days + "s" * (days != 1)
    elif hours > 0:
        return "%d hour" % hours + "s" * (hours != 1)
    elif minutes > 0:
        return "%d mn" % minutes + "s" * (minutes != 1)
    else:
        return "%.2f sec" % seconds + "s" * (seconds != 1)


def get_hashed_filename(filename):
    f_n, f_e = splitext(filename)

    fs_fname = hashlib.sha256()
    hashed_format = "%s-%s" % (f_n, datetime.datetime.now())
    fs_fname.update(hashed_format.encode("utf-8"))
    fs_fname = fs_fname.hexdigest()

    return fs_fname + f_e


def generate_random_token():
    t = hashlib.sha256()

    magic_sauce = "".join([random.choice(string.ascii_letters + string.digits) for n in range(250)])
    magic_sauce += str(datetime.datetime.now())

    t.update(magic_sauce.encode("utf-8"))
    return t.hexdigest()[:250]


def join_url(start, end):
    if end.startswith("http://") or end.startswith("https://"):
        # alread a full URL, joining makes no sense
        return end
    if start.endswith("/") and end.startswith("/"):
        return start + end[1:]

    if not start.endswith("/") and not end.startswith("/"):
        return start + "/" + end

    return start + end


# Also present in models.py, thx circle import
def strip_end(text, suffix):
    if not text.endswith(suffix):
        return text
    return text[: len(text) - len(suffix)]
