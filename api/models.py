import datetime

from flask import current_app
from flask_security import SQLAlchemyUserDatastore, UserMixin, RoleMixin
from flask_security.utils import verify_password
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import Comparator
from sqlalchemy.sql import func
from sqlalchemy_searchable import make_searchable
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from sqlalchemy import event


db = SQLAlchemy()
make_searchable(db.metadata)

# #### Base ####


class CaseInsensitiveComparator(Comparator):
    def __eq__(self, other):
        return func.lower(self.__clause_element__()) == func.lower(other)


# #### User ####

roles_users = db.Table(
    "roles_users",
    db.Column("user_id", db.Integer(), db.ForeignKey("user.id")),
    db.Column("role_id", db.Integer(), db.ForeignKey("role.id")),
)


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False, info={"label": "Name"})
    description = db.Column(db.String(255), info={"label": "Description"})

    __mapper_args__ = {"order_by": name}


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=True, info={"label": "Email"})
    name = db.Column(db.String(255), nullable=False, info={"label": "Username"})
    password = db.Column(db.String(255), nullable=True, info={"label": "Password"})
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    fs_uniquifier = db.Column(db.String(255))

    created_at = db.Column(db.DateTime(timezone=False), default=datetime.datetime.utcnow)
    updated_at = db.Column(
        db.DateTime(timezone=False), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )

    locale = db.Column(db.String(5), default="en")

    flake_id = db.Column(UUID(as_uuid=True), unique=False, nullable=True)

    slug = db.Column(db.String(255), nullable=True)

    # Relations

    roles = db.relationship(
        "Role", secondary=roles_users, backref=db.backref("users", lazy="dynamic"), cascade_backrefs=False
    )
    loggings = db.relationship("Logging", backref="user", lazy="dynamic", cascade="delete")

    __mapper_args__ = {"order_by": name}

    def is_admin(self):
        admin_role = db.session.query(Role).filter(Role.name == "admin").one()
        return admin_role in self.roles

    def join_roles(self, string):
        return string.join([i.description for i in self.roles])

    @staticmethod
    def generate_slug(target, value, oldvalue, initiator):
        if value and (not target.slug or value != oldvalue):
            target.slug = value

    def __repr__(self):
        return f"<User(id='{self.id}', name='{self.name}')>"

    def check_password(self, password):
        return verify_password(password, self.password)


event.listen(User.name, "set", User.generate_slug, retval=False)


@event.listens_for(User, "after_insert")
def generate_user_flakeid(mapper, connection, target):
    if not target.flake_id:
        flake_id = uuid.UUID(int=current_app.flake_id.get())
        connection.execute(User.__table__.update().where(User.__table__.c.id == target.id).values(flake_id=flake_id))


user_datastore = SQLAlchemyUserDatastore(db, User, Role)


class Logging(db.Model):
    __tablename__ = "logging"

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(255), nullable=False, default="General")
    level = db.Column(db.String(255), nullable=False, default="INFO")
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(
        db.DateTime(timezone=False), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )

    user_id = db.Column(db.Integer(), db.ForeignKey("user.id"), nullable=True)

    __mapper_args__ = {"order_by": timestamp.desc()}


# Item (main item)
class Item(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    flake_id = db.Column(UUID(as_uuid=True), unique=False, nullable=True)
    created_at = db.Column(db.DateTime(timezone=False), default=datetime.datetime.utcnow)
    openfoodfacts_id = db.Column(db.String(255))
    openfoodfacts_product = db.Column(JSONB())

    sub_items = db.relationship("SubItem", backref="item", lazy="dynamic", cascade="delete")


@event.listens_for(Item, "after_insert")
def generate_item_flakeid(mapper, connection, target):
    if not target.flake_id:
        flake_id = uuid.UUID(int=current_app.flake_id.get())
        connection.execute(Item.__table__.update().where(Item.__table__.c.id == target.id).values(flake_id=flake_id))


# Sub Item (qty, expiration)
class SubItem(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    qty = db.Column(db.Integer)
    expiry = db.Column(db.DateTime())
    created_at = db.Column(db.DateTime(timezone=False), default=datetime.datetime.utcnow)
    item_id = db.Column(db.Integer(), db.ForeignKey("item.id"), nullable=False)
