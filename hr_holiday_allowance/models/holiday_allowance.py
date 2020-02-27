from odoo import models, fields, exceptions, _
import datetime
from odoo import api
from odoo.exceptions import UserError, ValidationError

class HrHolidayAllowance(models.Model):
    _name = 'hr.holiday.allowance'
    _description = 'Holiday Allowance'
    _inherit = ['mail.thread']
    _rec_name = 'code'

    code = fields.Char("Allowance Code", required=True, readonly=True, copy=False, default='New')
    allowance_date = fields.Date("Allowance Date", required=True,
                                 states={'draft': [('readonly', False)],
                                         'confirmed': [('readonly', True)],
                                         'approved': [('readonly', True)],
                                         'cancel': [('readonly', True)]})
    start_time = fields.Datetime("Start Time", required=False,
                                 states={'draft': [('readonly', False)],
                                         'confirmed': [('readonly', True)],
                                         'approved': [('readonly', True)],
                                         'cancel': [('readonly', True)]})
    end_time = fields.Datetime("End Time", required=False,
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

    @api.multi
    def action_cancel(self):
        for record in self:
            record.state = 'cancel'
            for line in record.allowance_line:
                line.write({'state': 'cancel'})

    @api.model
    def create(self, vals):
        number = self.env['ir.sequence'].sudo().next_by_code('hr.holiday.allowance') or 'New'
        vals['code'] = number
        return super(HrHolidayAllowance, self).create(vals)

    def unlink(self):
        for line in self:
            if line.state != "draft":
                raise exceptions.UserError(
                    ('Cannot delete a record which is in state \'%s\'.') % (line.state,))
        return super(HrHolidayAllowance, self).unlink()



class HrHolidayAllowanceLine(models.Model):

    _name = 'hr.holiday.allowance.line'

    employee_id = fields.Many2one('hr.employee',string="Employee", required=True,
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

    def unlink(self):
        for line in self:
            if line.state != "draft":
                raise exceptions.UserError(
                    ('Cannot delete a Allowance Line which is in state \'%s\'.') % (line.state))
        return super(HrHolidayAllowanceLine, self).unlink()

    @api.constrains('employee_id')
    def __check_employee_id_validation(self):
        active_id = self.env.context.get('active_id')
        self._cr.execute(
            "SELECT employee_id FROM hr_holiday_allowance_line WHERE id != %s AND holiday_allowance_id = %s",
            tuple([self.id, active_id]))
        emp_data = self._cr.fetchall()
        if emp_data:
            emp_list = [data[0] for data in emp_data]
            if self.employee_id.id in emp_list:
                raise ValidationError(_(
                    "This employee is already selected: %s!!") % (
                    self.employee_id.name))

