#!/usr/bin/env python
from auth.app import Database, Util, FlaskApplication

Database.drop_all()
Database.create_all()

Util.create_character(FlaskApplication.config['ADMIN_CHARACTER_ID'])

Database.session.commit()
