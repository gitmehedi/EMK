from odoo import fields, models, api
from odoo.exceptions import ValidationError

class IndentType(models.Model):
    _name = "indent.type"
    _description = "Indent Type"
    _order = "id"

    name = fields.Char(string='Type Name',size=30)

    @api.constrains('name')
    def _check_unique_name(self):
        name = self.env['indent.type'].search(
            [('name', '=', self.name)])
        if len(name) > 1:
            raise ValidationError('This name is already existed')

