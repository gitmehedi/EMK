from odoo import fields, models, api, _
from odoo.exceptions import Warning

class ReportTypeSelectionModel(models.Model):
    _name = 'report.type.selection'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)
    status = fields.Boolean(default=True)

    @api.constrains('code')
    def _unique_code(self):
        code = self.search([('code','ilike',self.code)])

        if len(code)>1:
            raise Warning(_('Code should be unique.'))
