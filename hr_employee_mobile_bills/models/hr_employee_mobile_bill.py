from odoo import api, fields, models, _


class HrContract(models.Model):
    _inherit = 'hr.employee'

    mob_bill_unlimited = fields.Boolean('Unlimited')
    current_bill_limit = fields.Float(compute='_compute_current_limit', string='Current Limit', digits=(12, 2),
                                      help='The rate of the currency to the currency of rate 1.')

    """ All relations fields """
    mobile_bill_line_ids = fields.One2many('hr.employee.mobile.bill.line', 'employee_id', "Limits")

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

    @api.multi
    def name_get(self):
        display_mobile_dropdown = self.env.context.get('mobile_phone_dropdown')
        result = []
        if display_mobile_dropdown:
            for rec in self:
                if rec.mobile_phone:
                    name = rec.mobile_phone
                    result.append((rec.id, name))
                else:
                    result.append((rec.id, ''))
        else:
            for rec in self:
                name = unicode(rec.name) + ' [' + unicode(rec.job_id.name) + ']'
                result.append((rec.id, name))
        return result

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100):
        if args is None:
            args = []
        display_mobile_dropdown = self.env.context.get('mobile_phone_dropdown')
        operating_unit_id = self.env.context.get('operating_unit_id')
        company_id = self.env.context.get('company_id')
        if display_mobile_dropdown:
            domain = args + [('mobile_phone', operator, name), ('operating_unit_id', '=', operating_unit_id),
                             ('company_id', '=', company_id)]
        else:
            domain = args + [('name', operator, name)]
        return super(HrContract, self).search(domain, limit=limit).name_get()
