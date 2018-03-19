import time
from datetime import datetime, timedelta
from dateutil import relativedelta
import babel
from odoo import api, fields, models, tools, _

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.multi
    def onchange_employee(self):
        result = super(HrPayslip, self).onchange_employee()
        date_to = self.date_to
        if date_to:
            ttyme = datetime.fromtimestamp(time.mktime(time.strptime(date_to, "%Y-%m-%d")))
            locale = self.env.context.get('lang') or 'en_US'
            self.write({'name':_('Salary Slip of %s for %s') % (self.employee_id.name, tools.ustr(babel.dates.format_date(date=ttyme, format='MMMM-y', locale=locale)))})
        return result