from odoo import api, fields, models, _
from odoo.exceptions import Warning


class StockIssue(models.Model):
    _name = 'stock.issue.wizard'

    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit', required=True,
                                        default=lambda self: self.env.user.default_operating_unit_id)
    department_id = fields.Many2one('hr.department', string='Department')

    from_date = fields.Date('From', required=True)
    to_date = fields.Date('To', required=True)

    @api.multi
    def process_report(self):
        data = {
            'department_id': self.department_id.id,
            'department_name': self.department_id.name,
            'operating_unit_id': self.operating_unit_id.id,
            'operating_unit_name': self.operating_unit_id.name,
            'from_date': self.from_date,
            'to_date': self.to_date,
        }

        return self.env['report'].get_action(self, 'stock_issue_report.report_stock_issue', data=data)
