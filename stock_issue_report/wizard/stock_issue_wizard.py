from odoo import api, fields, models, _
from odoo.exceptions import Warning

class StockIssue(models.Model):
    _name = 'stock.issue.wizard'

    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit', required=True,
                                        default=lambda self: self.env.user.default_operating_unit_id)
    department_id = fields.Many2one('hr.department', string='Department')

    from_date = fields.Date('From',required=True)
    to_date = fields.Date('To',required=True)

    @api.constrains('to_date', 'from_date')
    def _check_date(self):
        if self.to_date and self.from_date:
            if self.from_date >= self.to_date:
                raise Warning("[Error] To Date must be greater than From Date!")