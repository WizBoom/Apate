from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.widgets import TextArea
from wtforms.validators import InputRequired


class RemoveApplicationForm(FlaskForm):
    rejection_reason = StringField('Rejection Reason', widget=TextArea(), validators=[InputRequired()])


class EditNoteForm(FlaskForm):
    notes = StringField('Notes', widget=TextArea())
