from .shared import Database


class User(Database.Model):

    id = Database.Column(Database.Integer, primary_key=True)
    name = Database.Column(Database.String)

    def __init__(self, name):
        self.name = name

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def __str__(self):
        return '<User-{}>'.format(self.name)
