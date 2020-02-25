from odoo import models, fields, exceptions, _
import datetime
from odoo import api
from odoo.exceptions import UserError, ValidationError

class HrHolidayAllowance(models.Model):
    _name = 'hr.holiday.allowance'
    _description = 'Hr Holiday Allowance'
    _inherit = ['mail.thread']
    _rec_name = 'code'

    code = fields.Char("Allowance Code", required=True, readonly=True, copy=False, default='New')
    allowance_date = fields.Date("Allowance Date", required=True,
                                 states={'draft': [('readonly', False)],
                                         'confirmed': [('readonly', True)],
                                         'approved': [('readonly', True)],
                                         'cancel': [('readonly', True)]})
    description = description = fields.Char("Description")
    allowance_line = fields.One2many('hr.holiday.allowance.line', 'holiday_allowance_id', string="Employees", copy=True, auto_join=True)
    state = fields.Selection([
        ('draft', "Draft"),
        ('confirmed', "Confirmed"),
        ('approved', "Approved"),
        ('cancel', 'Cancelled')
    ], default='draft', track_visibility='onchange')

    @api.multi
    def action_confirm(self):
        for record in self:
            if not record.allowance_line:
                raise ValidationError(_('Please select at least one employee before confirming!!'))
            record.state = 'confirmed'
            if record.allowance_line:
                for line in record.allowance_line:
                    vals = {
                        'emp_allowance_date': record.allowance_date,
                        'state': 'confirmed'
                    }
                    line.write(vals)
            return record

    @api.multi
    def action_approve(self):
        for record in self:
            record.state = 'approved'
            for line in record.allowance_line:
                line.write({'state': 'approved'})

    @api.model
    def create(self, vals):
        number = self.env['ir.sequence'].sudo().next_by_code('hr.holiday.allowance') or 'New'
        vals['code'] = number
        return super(HrHolidayAllowance, self).create(vals)




class HrHolidayAllowanceLine(models.Model):

    _name = 'hr.holiday.allowance.line'

    employee_id = fields.Many2one('hr.employee',string="Employee",
                                  states={'draft': [('readonly', False)],
                                         'confirmed': [('readonly', True)],
                                         'approved': [('readonly', True)],
                                         'cancel': [('readonly', True)]})
    emp_allowance_date = fields.Date('Allowance Date', readonly=True)
    holiday_allowance_id = fields.Many2one('hr.holiday.allowance', string='Holliday Allowance ID', ondelete='cascade', index=True, copy=False, required=True, readonly=True)
    state = fields.Selection([
        ('draft', "Draft"),
        ('confirmed', "Confirmed"),
        ('approved', "Approved"),
        ('cancel', 'Cancelled')
    ], default='draft', track_visibility='onchange')

