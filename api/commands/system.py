import click
import sys
from flask.cli import with_appcontext
from flask_mail import Message
from flask import render_template, current_app
import texttable
from pprint import pprint as pp


@click.group()
def system():
    """
    System commands.
    """
    pass


@system.command(name="config")
@with_appcontext
def config():
    """
    Dump config
    """
    pp(current_app.config)


@system.command(name="test-email")
@click.option("--email", prompt=True, help="Email to send the test to")
@with_appcontext
def test_email(email):
    """
    Test email sending.
    """
    mail = current_app.extensions.get("mail")
    if not mail:
        print("ERROR: mail extensions is None !!!")
        exit(-1)

    msg = Message(
        subject="omnomnomnom test email", recipients=[email], sender=current_app.config["MAIL_DEFAULT_SENDER"]
    )
    msg.body = render_template("email/test_email.txt")
    msg.html = render_template("email/test_email.html")
    try:
        mail.send(msg)
    except:  # noqa: E722
        print(f"Error sending mail: {sys.exc_info()[0]}")


@system.command(name="routes")
@with_appcontext
def routes():
    """
    Dump all routes of defined app
    """
    table = texttable.Texttable()
    table.set_deco(texttable.Texttable().HEADER)
    table.set_cols_dtype(["t", "t", "t"])
    table.set_cols_align(["l", "l", "l"])
    table.set_cols_width([50, 30, 80])

    table.add_rows([["Prefix", "Verb", "URI Pattern"]])

    for rule in sorted(current_app.url_map.iter_rules(), key=lambda x: str(x)):
        methods = ",".join(rule.methods)
        table.add_row([rule.endpoint, methods, rule])

    print(table.draw())
