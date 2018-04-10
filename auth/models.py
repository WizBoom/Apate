from .shared import Database, SharedInfo

# -- Connections -- #
permissionConnection = Database.Table(
    'PermissionConnection',
    Database.Column('role_id', Database.Integer, Database.ForeignKey('Roles.id')),
    Database.Column('permission_id', Database.Integer, Database.ForeignKey('Permissions.id')))

roleConnection = Database.Table(
    'RolesConnection',
    Database.Column('character_id', Database.Integer, Database.ForeignKey('Characters.id')),
    Database.Column('role_id', Database.Integer, Database.ForeignKey('Roles.id')))
# -- End Connections -- #

# -- Classes -- #


class Character(Database.Model):
    __tablename__ = 'Characters'
    id = Database.Column(Database.Integer, primary_key=True)
    name = Database.Column(Database.String)
    corp_id = Database.Column(Database.Integer, Database.ForeignKey('Corporations.id'))

    def __init__(self, id, name):
        self.id = id
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

    def get_corp(self):
        return Corporation.query.filter_by(id=self.corp_id).first()

    def has_permission(self, permission_name):
        # Loop over roles to see if any of the roles have the correct permission
        for role in self.roles:
            if role.has_permission(permission_name):
                return True

        # If nothing was found, return false
        return False

    @property
    def is_in_alliance(self):
        return self.get_corp().alliance_id == SharedInfo['alliance_id']

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
    alliance_id = Database.Column(Database.Integer, Database.ForeignKey('Alliances.id'))
    characters = Database.relationship('Character', backref='Corporation', lazy='dynamic', cascade="all, delete-orphan")

    def get_alliance(self):
        return Alliance.query.filter_by(id=self.alliance_id).first()

    def __init__(self, id, name, ticker, logo):
        self.id = id
        self.name = name
        self.ticker = ticker
        self.logo = logo

    def __repr__(self):
        return '<Corporation-{} [{}]>'.format(self.name, self.ticker)


class Permission(Database.Model):
    __tablename__ = 'Permissions'
    id = Database.Column(Database.Integer, primary_key=True)
    name = Database.Column(Database.String, nullable=False)
    roles = Database.relationship('Role', secondary=permissionConnection, backref=Database.backref('permissions', lazy='dynamic'))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Permission-{}>'.format(self.name)


class Role(Database.Model):
    __tablename__ = 'Roles'
    id = Database.Column(Database.Integer, primary_key=True)
    name = Database.Column(Database.String, nullable=False, unique=True)
    characters = Database.relationship('Character', secondary=roleConnection, backref=Database.backref('roles', lazy='dynamic'))

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return '<Role-{}>'.format(self.name)

    def has_permission(self, permission_name):
        # Get permission list
        permissionNames = [permission.name.lower() for permission in self.permissions]
        return permission_name.lower() in permissionNames
# -- End Classes -- #
