import click
from models import db, Role
from flask.cli import with_appcontext


@click.group()
def db_datas():
    """
    Datas migrations sometimes needed.

    Run them only one time unless specified BREAKING.
    """
    pass


def make_db_seed(db):
    # roles
    roles = db.session.query(Role.name).all()
    roles = [r[0] for r in roles]
    if "user" not in roles:
        role_usr = Role(name="user", description="Simple user")
        db.session.add(role_usr)
    if "admin" not in roles:
        role_adm = Role(name="admin", description="Admin user")
        db.session.add(role_adm)

    # Final commit
    db.session.commit()


@db_datas.command(name="000-seeds")
@with_appcontext
def seeds():
    """
    Seed database with default config and roles values

    non breaking.
    """
    make_db_seed(db)
