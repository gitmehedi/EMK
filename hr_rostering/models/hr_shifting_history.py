from openerp import fields,api,models,_
from odoo.exceptions import UserError, ValidationError
from datetime import date,datetime, timedelta


class HrShiftingHistory(models.Model):
    _name = 'hr.shifting.history'
    _order = "id DESC"
    _list_id = 0

    """ Required and Optional fields """
    effective_from = fields.Date(string='Effective Date', required=True)
    effective_end = fields.Date(string='Effective End Date', required=True)


    """ Relational Fields """
    employee_id = fields.Many2one("hr.employee", string='Employee Name', required=True)
    shift_id = fields.Many2one("resource.calendar", string="Shift Name", required=True ,domain="[('state', '=','approved' )]")

    """Shift Batch Relational Fields """
    shift_batch_id =fields.Many2one('hr.shift.employee.batch', string='Shift Batch')

    @api.constrains('effective_end')
    def _check_effective_end_validation(self):
        if self.effective_end > self.effective_from:
            pass
        else:
            raise ValidationError(_("Effective To date can not less then Effective From date!!"))

    @api.constrains('effective_from')
    def _check_effective_from_validation(self):
        query = """select max(effective_end) from hr_shifting_history WHERE id != %s AND employee_id = %s"""
        self._cr.execute(query, tuple([self.id, self.employee_id.id]))
        get_previous_row_effective_to_date = self._cr.fetchone()
        if get_previous_row_effective_to_date:
            str_previous_effective_to = get_previous_row_effective_to_date[0]
            if str_previous_effective_to:
                date_previous_effective_to = datetime.strptime(str_previous_effective_to, "%Y-%m-%d")
                ranged_last_date = date_previous_effective_to + timedelta(days=1)
                emp_name=self.employee_id.name
                print emp_name
                if self.effective_from <= str_previous_effective_to:
                    raise ValidationError(_("Current Effective date can not less then previous Effective date!! Already %s has a shift") % emp_name)
                elif datetime.strptime(self.effective_from, "%Y-%m-%d") == ranged_last_date:
                    pass
                else:
                    raise ValidationError(_("Current Effective date should not be too far from previous effective date!!"))

    # @api.onchange('effective_from')
    # def _onchange_effective_from(self):
    #     # print "---------------------- Lists--------------------", self.employee_id.id
    #     if self.effective_from and self.employee_id and self.shift_id:
    #         self.effective_from
    #         shifting = self.env['hr.shifting.history'].search([('employee_id', '=', self.employee_id.id),
    #                                                                ('effective_from', '<=', self.effective_from)], order='effective_from desc', limit=1)
    #         if shifting:
    #             print "---------------- Calling -------------------", shifting.id
    #             effective_from_tmp = int(datetime.datetime.strptime(self.effective_from, '%Y-%m-%d').strftime("%s"))
    #             effective_end_tmp = datetime.datetime.fromtimestamp(effective_from_tmp - 86400).strftime('%Y-%m-%d')
    #
    #             for shift in shifting:
    #                 shift.effective_end = effective_end_tmp
