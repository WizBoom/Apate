#!/usr/bin/env python
from auth.app import Database
from auth.models import *


Database.drop_all()
Database.create_all()
character = Character(92399833, 'Alex Kommorov')
Database.session.add(character)

corporation = Corporation(98134538, "Wormbro", "NW0RT", "")
Database.session.add(corporation)
corporation.characters.append(character)

alliance = Alliance(99006650, "The Society For Unethical Treatment Of Sleepers", "GETIN", "")
Database.session.add(alliance)
alliance.corporations.append(corporation)

Database.session.commit()
