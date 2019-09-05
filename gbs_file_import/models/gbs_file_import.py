from odoo import api, models, fields, _
from odoo.exceptions import ValidationError


class GBSFileImport(models.Model):
    _name = 'gbs.file.import'
    _inherit = ['mail.thread']
    
    name = fields.Char(string='Title', required=True,track_visibility='onchange')
    import_creation_date_time = fields.Datetime(string='Date',default=fields.Datetime.now,track_visibility='onchange')

    """ Relational fields"""
    import_lines = fields.One2many('gbs.file.import.line', 'import_id')

    _sql_constraints = [
        ('name_unique', 'unique (name)', 'Cannot duplicate the name !')
    ]

    def action_process(self):
        raise ValidationError(_('Work on process.'))



class GBSFileImportLine(models.Model):
    _name = 'gbs.file.import.line'

    name = fields.Char(string='Account Name')
    state = fields.Char(string='Status')
    type = fields.Char(string='Type')

    import_id = fields.Many2one('gbs.file.import', 'Import Id', ondelete='cascade')