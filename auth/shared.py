from flask_sqlalchemy import SQLAlchemy

Database = SQLAlchemy()
SharedInfo = {
    'alliance_id': 0,
    'util': None
}
EveAPI = {
    'user_agent': "",
    'default_user_preston': None,
    'corp_preston': None,
    'full_auth_preston': None
}
