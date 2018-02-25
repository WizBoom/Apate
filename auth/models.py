from .shared import Database


class Character(Database.Model):
    __tablename__ = 'Characters'
    id = Database.Column(Database.Integer, primary_key=True)
    name = Database.Column(Database.String)
    corpId = Database.Column(Database.Integer, Database.ForeignKey('Corporations.id'))

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
        return str(self.character_id)

    def __str__(self):
        return '<Character-{}>'.format(self.name)


class Alliance(Database.Model):
    __tablename__ = 'Alliances'
    id = Database.Column(Database.Integer, primary_key=True)
    name = Database.Column(Database.String, nullable=False)
    ticker = Database.Column(Database.String, nullable=False)
    logo = Database.Column(Database.String, nullable=False)
    corporations = Database.relationship('Corporation', backref='Alliance', lazy='dynamic', cascade="all, delete-orphan")

    def __init__(self, id, name, ticker, logo):
        self.id = id
        self.name = name
        self.ticker = ticker
        self.logo = logo

    def __repr__(self):
        return '<Alliance-{} [{}]>'.format(self.name, self.ticker)


class Corporation(Database.Model):
    __tablename__ = 'Corporations'
    id = Database.Column(Database.Integer, primary_key=True)
    name = Database.Column(Database.String, nullable=False)
    ticker = Database.Column(Database.String, nullable=False)
    logo = Database.Column(Database.String, nullable=False)
    allianceId = Database.Column(Database.Integer, Database.ForeignKey('Alliances.id'))
    characters = Database.relationship('Character', backref='Corporation', lazy='dynamic', cascade="all, delete-orphan")

    def __init__(self, id, name, ticker, logo):
        self.id = id
        self.name = name
        self.ticker = ticker
        self.logo = logo

    def __repr__(self):
        return '<Corporation-{} [{}]>'.format(self.name, self.ticker)
