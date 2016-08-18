from openerp import models, fields, api, exceptions
from openerp.osv import osv
import datetime


class petty_cash_reimbursement(models.Model):
    _name = 'petty.cash.reimbursement'

    name = fields.Char(string='Name')
    branch_id = fields.Many2one('res.branch', string='Branch Name', rquired=True)
    received_by = fields.Many2one('res.users', string='Received By', rquired=True)
    amount = fields.Float(digits=(20, 3), string="Amount", rquired=True)
    received_date = fields.Date()
    state = fields.Selection([('draft', 'Draft'), ('received', 'Received'), ],
                             'Status', select=True,
                             readonly=True,
                             default='draft')

    @api.multi
    def action_submit(self):
        return self.write({'state': 'received'})

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state not in ['draft']:
                raise osv.except_osv(_('Warning!'), _('You cannot delete! It is in %s state.') % (rec.state))
        return super(EmployeeExitReq, self).unlink()

