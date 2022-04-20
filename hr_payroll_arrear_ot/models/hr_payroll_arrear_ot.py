from odoo import api, fields, models


class InheritedHrEmployeeArrear(models.Model):
    _inherit = 'hr.payroll.arrear'
    _order = 'id DESC'


    type = fields.Selection([
        ('regular', 'Regular'),
        ('ot', 'OT'),
    ], string='Type',default='regular', required=True)


class InheritedHrEmployeeArrearLine(models.Model):
    _inherit = 'hr.payroll.arrear.line'


    type = fields.Selection([
        ('regular', 'Regular'),
        ('ot', 'OT'),
    ], string='Type',default='regular', required=True)

    @api.model
    def create(self, vals):
        """Override to set type of arrear line create based on arrear"""
        res = super(InheritedHrEmployeeArrearLine, self).create(vals)
        hr_payroll_arrear = self.env['hr.payroll.arrear'].search([('id', '=', res.parent_id.id)])
        if hr_payroll_arrear.type == 'regular':
            res.update({
                'type': 'regular'
            })
        elif hr_payroll_arrear.type == 'ot':
            res.update({
                'type': 'ot'
            })
        return res


    @api.multi
    def write(self, vals):
        """Override to set type of arrear line update based on arrear"""
        hr_payroll_arrear = self.env['hr.payroll.arrear'].search([('id', '=', self.parent_id.id)])
        if hr_payroll_arrear.type == 'regular':
            vals['type'] = 'regular'
        elif hr_payroll_arrear.type == 'ot':
            vals['type'] = 'ot'
        res = super(InheritedHrEmployeeArrearLine, self).write(vals)
        return res

