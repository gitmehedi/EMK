from openerp import models, fields, api
from openerp.exceptions import Warning
from openerp.osv import osv

class HrHolidaysExtended(models.Model):
    _inherit = 'hr.holidays'

    name = fields.Text(string='Description')
    #number_of_days = fields.Float(compute='_compute_number_of_days', string='Number of Days'),

    officer_id = fields.Many2one('res.users', string='HR Officer', compute='_get_officer_id', store=True)

    state = fields.Selection(
        [('draft', 'To Submit'), ('cancel', 'Cancelled'), ('confirm', 'To Approve'), ('refuse', 'Refused'),
         ('validate1', 'Second Approval'), ('validate', 'Approved')],
        'Status', readonly=True, copy=False, default='draft',
        help='The status is set to \'To Submit\', when a holiday request is created.\
            \nThe status is \'To Approve\', when holiday request is confirmed by user.\
            \nThe status is \'Refused\', when holiday request is refused by manager.\
            \nThe status is \'Approved\', when holiday request is approved by manager.')

    @api.depends('employee_id')
    def _get_officer_id(self):
        if (self.employee_id.parent_id):
            self.officer_id = self.employee_id.parent_id.user_id.id

    @api.multi
    @api.depends('date_from')
    def _compute_number_of_days(self):
        print 'heloo debug'
        raise osv.except_osv(_('Warning!'), _('Please provide right values'))

        result = {}
        for hol in self.browse(self.ids):
            diff_day = self._get_number_of_days(hol.date_from, hol.date_to)
            day = round(math.floor(diff_day)) + 1
            if hol.number_of_days_temp <= day:
                if hol.type == 'remove':
                    result[hol.id] = -hol.number_of_days_temp
                else:
                    result[hol.id] = hol.number_of_days_temp
            else:
                raise osv.except_osv(_('Warning!'), _('Please provide right values'))

        return result
    #
    # @api.model
    # def create(self, vals):
    #     raise osv.except_osv(_('Warning!'), _('tttttttt Please provide right values'))
    #
    #     return True
