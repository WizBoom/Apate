from flask_sqlalchemy import SQLAlchemy

Database = SQLAlchemy()
SharedInfo = {
    'alliance_id': 0,
}
EveAPI = {
    'user_agent': "",
    'default_user_preston': None,
    'corp_preston': None
}
