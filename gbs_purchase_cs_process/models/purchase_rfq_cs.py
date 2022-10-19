from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PurchaseRFQCS(models.Model):
    _name = "purchase.rfq.cs"

    rfq_id = fields.Many2one('purchase.rfq', string='RFQ')
    operating_unit_id = fields.Many2one('operating.unit', 'Select Operating Unit',
                                        default=lambda self: self.env.user.default_operating_unit_id)
    department_id = fields.Many2one("hr.department", string="Department")
    employee_id = fields.Many2one("hr.employee", string="Employee")
    from_date = fields.Date(string='From Date')
    to_date = fields.Date(string='To Date')

