from odoo import api, fields, models, _

class HrContract(models.Model):

    _inherit = 'hr.employee'

    mob_bill_unlimited = fields.Boolean('Unlimited')
    current_bill_limit = fields.Float(compute='_compute_current_limit', string='Current Limit', digits=(12, 2),
                                      help='The rate of the currency to the currency of rate 1.')

    """ All relations fields """
    mobile_bill_line_ids =fields.One2many('hr.employee.mobile.bill.line','employee_id',"Limits")

    @api.multi
    def _compute_current_limit(self):
        date = self._context.get('date') or fields.Datetime.now()
        # the subquery selects the last rate before 'date' for the given currency/company
        query = """SELECT e.id, (SELECT l.limit FROM hr_employee_mobile_bill_line l
                                  WHERE l.employee_id = e.id AND l.effective_date <= %s
                                  ORDER BY l.employee_id, l.effective_date DESC
                                  LIMIT 1) AS limit
                       FROM hr_employee e
                       WHERE e.id IN %s"""
        self._cr.execute(query, (date, tuple(self.ids)))
        limits = dict(self._cr.fetchall())
        for emp in self:
            emp.current_bill_limit = limits.get(emp.id) or 0.0