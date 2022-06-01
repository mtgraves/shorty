from flask import request
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Optional
from wtforms import StringField, SubmitField, BooleanField

class SearchForm(FlaskForm):
    q = StringField('Search', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)


class NewLinkForm(FlaskForm):

    enter_link = StringField('Enter your URL to convert',
            validators = [DataRequired()]
            )

    request_url_suffix_true = BooleanField('Request URL Suffix')
    request_url_suffix = StringField('Desired URL suffix',
            validators = [Optional()]
            )

    submit = SubmitField('Facilitate my laziness')

    # extend default form validation
    def validate(self):
        super().validate()
        result = True

        # ensure priority falls within a sane range
        must_start_with = ['http:','https:']
        url_protocol_error_message = 'your URL must start with http:// or https://'

        if self.enter_link.data != None:
            if self.enter_link.data.split('//')[0] not in must_start_with:
                # otherwise throw them validation errorsssss
                self.enter_link.errors.append(url_protocol_error_message)
                result = False

        # if user clicks 'new program' then ensure one is chosen
        request_url_error_message = 'enter requested URL or uncheck box'

        # no new url input AND requested url checkbox = checked
        if self.request_url_suffix.data == '' and self.request_url_suffix_true.data == True:
            # throw errors
            self.request_url_suffix_true.errors = [request_url_error_message]
            result = False
    
        return result
