from odoo import api, fields, models, _


class StockIssue(models.Model):
    _name = 'stock.issue.wizard'

    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit', required=True,
                                        default=lambda self: self.env.user.default_operating_unit_id)
    from_date = fields.Date('From', required=True)
    to_date = fields.Date('To', required=True)

    @api.multi
    def process_report(self):
        data = {}
        data['operating_unit_id'] = self.operating_unit_id.id
        data['operating_unit_name'] = self.operating_unit_id.name
        data['from_date'] = self.from_date
        data['to_date'] = self.to_date

        return self.env['report'].get_action(self, 'stock_issue_report.report_stock_issue', data=data)
