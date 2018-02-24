#!/usr/bin/env python
from auth.app import db
from auth.models import *


db.drop_all()
db.create_all()
u = User('Alex Kommorov')
db.session.add(u)
db.session.commit()
