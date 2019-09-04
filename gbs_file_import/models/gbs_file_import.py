from datetime import date
from odoo import api, models, fields

class GBSFileImport(models.Model):
    _name = 'gbs.file.import'
    
    name = fields.Char(string='Title', required=True)
    import_creation_date_time = fields.Datetime(string='Date',default=fields.Datetime.now)

    """ Relational fields"""
    import_lines = fields.One2many('gbs.file.import.line', 'import_id')




class GBSFileImportLine(models.Model):
    _name = 'gbs.file.import.line'

    name = fields.Char(string='Description')
    state = fields.Char(string='Status')
    type = fields.Char(string='Type')

    import_id = fields.Many2one('gbs.file.import', 'Import Id', ondelete='cascade')