import click
from models import db, user_datastore, Role, User
from flask.cli import with_appcontext
from flask import current_app
from flask_security.utils import hash_password
from flask_security import confirmable as FSConfirmable
import texttable
import datetime


@click.group()
def users():
    """
    User commands.
    """
    pass


@users.command(name="list")
@with_appcontext
def list():
    """
    List local users.
    """
    users = User.query.filter()

    table = texttable.Texttable(max_width=120)
    table.set_deco(texttable.Texttable().HEADER)
    table.set_cols_dtype(["i", "t"])
    table.set_cols_align(["l", "l"])
    table.add_rows([["ID", "username"]])

    for user in users.all():
        table.add_row(
            [user.id, user.name,]
        )

    print(table.draw())


@users.command(name="create")
@with_appcontext
def create():
    """
    Create a user.
    """
    username = click.prompt("Username", type=str)
    email = click.prompt("Email", type=str)
    password = click.prompt("Password", type=str, hide_input=True, confirmation_prompt=True)
    while True:
        role = click.prompt("Role [admin/user]", type=str)
        if role == "admin" or role == "user":
            break

    if click.confirm("Do you want to continue ?"):
        role = Role.query.filter(Role.name == role).first()
        if not role:
            raise click.UsageError("Roles not present in database")
        u = user_datastore.create_user(name=username, email=email, password=hash_password(password), roles=[role])

        db.session.commit()

        if FSConfirmable.requires_confirmation(u):
            with current_app.app_context():
                FSConfirmable.send_confirmation_instructions(u)
                print("Look at your emails for validation instructions.")


@users.command(name="confirm")
@click.option("--username", prompt=True, help="Username")
@with_appcontext
def confirm(username):
    """
    Force activation of an user.
    """
    u = User.query.filter(User.name == username).first()
    if not u:
        print(f"Cannot find user with username '{username}'")
        exit(1)

    u.confirmed_at = datetime.datetime.now()
    db.session.commit()

    print("User confirmed at: ", u.confirmed_at)
