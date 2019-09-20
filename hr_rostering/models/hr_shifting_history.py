from openerp import fields,api,models,_
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta


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
        if self.effective_end < self.effective_from:
            raise ValidationError(_("Effective End date can not less then Effective From date!!"))


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
                if self.effective_from <= str_previous_effective_to:
                    raise ValidationError(_("Current Effective date can not less then previous Effective date!! Already %s has a shift. His effective end date %s") % (emp_name,str_previous_effective_to))
                elif datetime.strptime(self.effective_from, "%Y-%m-%d") == ranged_last_date:
                    pass
                else:
                    raise ValidationError(_("Current Effective date should not be too far from previous effective date!! %s effective end date %s .")%(emp_name,str_previous_effective_to))