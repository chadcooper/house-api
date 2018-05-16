from wtforms import Form, StringField, SelectField


class ItemForm(Form):
    description = StringField('Description')
    room = StringField('Room')