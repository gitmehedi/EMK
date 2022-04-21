from odoo import api, fields, models


class InheritedHrEmployeeOtherDeduction(models.Model):
    _inherit = 'hr.other.deduction'
    _order = 'id DESC'


    type = fields.Selection([
        ('regular', 'Regular'),
        ('ot', 'OT'),
    ], string='Type',default='regular', required=True)


class InheritedHrOtherDeductionLine(models.Model):
    _inherit = 'hr.other.deduction.line'


    type = fields.Selection([
        ('regular', 'Regular'),
        ('ot', 'OT'),
    ], string='Type', default='regular', required=True)

    @api.model
    def create(self, vals):
        """Override to set type of deduction line create based on deduction"""
        res = super(InheritedHrOtherDeductionLine, self).create(vals)
        hr_other_deduction = self.env['hr.other.deduction'].search([('id', '=', res.parent_id.id)])
        if hr_other_deduction.type == 'regular':
            res.update({
                'type': 'regular'
            })
        elif hr_other_deduction.type == 'ot':
            res.update({
                'type': 'ot'
            })
        return res

    @api.multi
    def write(self, vals):
        """Override to set type of other deduction line update based on deduction"""
        hr_other_deduction = self.env['hr.other.deduction'].search([('id', '=', self.parent_id.id)])
        if hr_other_deduction.type == 'regular':
            vals['type'] = 'regular'
        elif hr_other_deduction.type == 'ot':
            vals['type'] = 'ot'
        res = super(InheritedHrOtherDeductionLine, self).write(vals)
        return res

