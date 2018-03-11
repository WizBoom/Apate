#!/usr/bin/env python
from auth.app import Database, Util

Database.drop_all()
Database.create_all()

Util.create_character(92399833)

Database.session.commit()
