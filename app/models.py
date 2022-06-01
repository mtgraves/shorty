from app import db, login
from flask_login import UserMixin
from app.search import add_to_index, remove_from_index, query_index


# =============================================================================
class SearchableMixin(object):
    @classmethod
    def search(cls, expression, page, per_page):
        ids, total = query_index(cls.__tablename__, expression, page, per_page)
        if total == 0:
            return cls.query.filter_by(id=0), 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        return cls.query.filter(cls.id.in_(ids)).order_by(
            db.case(when, value=cls.id)), total

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)

db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)


# =============================================================================                    
class RandomLinkTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, 
            db.ForeignKey('user_table.id'))
    original_url = db.Column(db.String(512))
    new_url = db.Column(db.String(512))
    new_url_suffix = db.Column(db.String(256))
    date_created = db.Column(db.DateTime)

    # relationships
    associated_user = db.relationship('UserTable')


# =============================================================================                    
class RequestedLinkTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, 
            db.ForeignKey('user_table.id'))
    original_url = db.Column(db.String(512))
    new_url = db.Column(db.String(512))
    new_url_suffix = db.Column(db.String(256))
    date_created = db.Column(db.DateTime)

    # relationships
    associated_user = db.relationship('UserTable')


# =============================================================================                    
class RolesTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(64))


# =============================================================================                    
class UserRolesTable(db.Model):
    
    # fields
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, 
            db.ForeignKey('user_table.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer, 
            db.ForeignKey('roles_table.id', ondelete='CASCADE'))

    # relationships
    associated_user = db.relationship('UserTable')


# =============================================================================                    
class UserStatusTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status_name = db.Column(db.String(16))


# =============================================================================                    
class UserTable(UserMixin, db.Model):
    
    # fields
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    lastname = db.Column(db.String(64))
    firstname = db.Column(db.String(64))
    email = db.Column(db.String(64), unique=True)
    phone = db.Column(db.String(32))
    user_status = db.Column(db.Integer, db.ForeignKey('user_status_table.id'))

    # relationships
    roles = db.relationship('RolesTable', secondary='user_roles_table')
    associated_status = db.relationship('UserStatusTable')

    # functions
    def __repr__(self):
        return '<User {}>'.format(self.username)


# =============================================================================                    
@login.user_loader
def load_user(id):
    return UserTable.query.get(int(id))
