from datetime import date, datetime
from openerp import models, fields,_
from openerp import api
from openerp.exceptions import UserError, ValidationError
from datetime import timedelta

class AttendanceImport(models.Model):
    _name = 'hr.attendance.import'
    
    name = fields.Char(string='Name', required=True)
    import_creation_date_time = fields.Datetime(string='Imported Date',default=date.today(),required=True)
    
    state = fields.Selection([
        ('draft', "Draft"),
        ('validate', "Validate"),
        ('confirmed', "Confirmed"),
        ('imported', "Imported")
    ], default='draft')
    
    """ Relational fields"""
    import_temp = fields.One2many('hr.attendance.import.temp', 'import_id', states={'imported': [('readonly', True)]})
    import_error_lines = fields.One2many('hr.attendance.import.error', 'import_id', states={'imported': [('readonly', True)]})
    lines = fields.One2many('hr.attendance.import.line', 'import_id', states={'imported': [('readonly', True)]})
    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit', required=True)

    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.user.company_id)

    @api.multi
    def action_approve(self):

        attendance_obj = self.env['hr.attendance']
        
        """ Fetch all from line obj"""
        attendance_line_obj = self.env['hr.attendance.import.line'].search([('import_id','=',self.id)])
        
        is_success = False

        for i in attendance_line_obj:
            if i is not None:
                emp_pool = self.env['hr.employee'].search([('id','=',i.employee_id.id)])

                vals_attendance = {}
                vals_attendance['employee_id'] = i.employee_id.id
                vals_attendance['check_in'] = i.check_in
                vals_attendance['check_out'] = i.check_out

                attendance_obj.create(vals_attendance)

                is_success = True

            if is_success is True:
                self.state = 'imported'

    @api.multi
    def action_confirm(self):
        import_line = self.env['hr.attendance.import.error'].search([('import_id', '=', self.id)])
        if import_line:
            raise ValidationError(
                _("Before apply please solve error data's row data"))

        self.state = 'confirmed'

    @api.multi
    def action_validate(self):
        self._check_time()
        self.state = 'validate'

    @api.multi
    def action_reset_to_draft(self):
        self.state = 'draft'

    # Show a msg for applied & approved state should not be delete
    @api.multi
    def unlink(self):
        for imp in self:
            if imp.state != 'draft':
                raise UserError(_('You can not delete this.'))
            imp.lines.unlink()
        return super(AttendanceImport, self).unlink()


    def _check_time(self):
        sl_pool = self.env["hr.short.leave"]
        att_pool = self.env["hr.attendance"]
        att_line = self.env["hr.attendance.import.line"].search([('import_id', '=', self.id)])
        for h in att_line:
            domain = [
                ('check_in', '<', h.check_out),
                ('check_out', '>', h.check_in),
                ('employee_id', '=', h.employee_id.id),
                ('id', '!=', h.id),
            ]
            sl_domain = [
                ('date_from', '<', h.check_out),
                ('date_to', '>', h.check_in),
                ('employee_id', '=', h.employee_id.id),
                ('id', '!=', h.id),
                ('state', 'not in', ['cancel', 'refuse']),
            ]
            att_domain = [
                ('check_in', '<', h.check_out),
                ('check_out', '>', h.check_in),
                ('employee_id', '=', h.employee_id.id),
                ('id', '!=', h.id),
            ]
            check_manual_att = att_line.search_count(domain)
            import_line = self.env['hr.attendance.import.error'].search([('ref_id', '=', h.id)])
            if check_manual_att and not import_line:
                self.env['hr.attendance.import.error'].create({
                    'import_id': self.id,
                    'employee_id': h.employee_id.id,
                    'acc_no': int(h.acc_no),
                    'check_in': h.check_in,
                    'check_out': h.check_out,
                    'ref_id': h.id
                })
                h.unlink()
                continue

            check_sl = sl_pool.search_count(sl_domain)
            if check_sl and not import_line:
                self.env['hr.attendance.import.error'].create({
                    'import_id': self.id,
                    'employee_id': h.employee_id.id,
                    'acc_no': int(h.acc_no),
                    'check_in': h.check_in,
                    'check_out': h.check_out,
                    'ref_id': h.id
                })
                h.unlink()
                continue

            check_att = att_pool.search_count(att_domain)
            if check_att and not import_line:
                self.env['hr.attendance.import.error'].create({
                    'import_id': self.id,
                    'employee_id': h.employee_id.id,
                    'acc_no': int(h.acc_no),
                    'check_in': h.check_in,
                    'check_out': h.check_out,
                    'ref_id': h.id
                })
                h.unlink()
                continue