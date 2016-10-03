from openerp import models,fields


class more_formats(models.Model):
    _name='more.formats'
    name=fields.Char('Formats Name')
    date_format=fields.Char('Date Format',required=True)
    time_format=fields.Char('Time Format',required=True)


    def _get_default_date_format(self, cursor, user, context=None):
        return '%m/%d/%Y'

    def _get_default_time_format(self, cursor, user, context=None):
        return '%H:%M:%S'

    _defaults = {
        'date_format':_get_default_date_format,
        'time_format':_get_default_time_format,
    }
    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The name of the language must be unique !')
     ]

more_formats()