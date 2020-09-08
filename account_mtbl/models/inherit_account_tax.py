from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import ValidationError
from psycopg2 import IntegrityError


class AccountTax(models.Model):
    _name = 'account.tax'
    _order = 'name desc'
    _inherit = ['account.tax', 'mail.thread']

    # pending = fields.Boolean(string='Pending', default=True, track_visibility='onchange',
    #                          states={'draft': [('readonly', False)]})
    # active = fields.Boolean(string='Active', default=False, track_visibility='onchange', readonly=True,
    #                         states={'draft': [('readonly', False)]})
    # state = fields.Selection([('draft', 'Draft'), ('approve', 'Approved'), ('reject', 'Rejected')], default='draft',
    #                          string="Status", track_visibility='onchange')
    # history_ids = fields.One2many('history.account.tax', 'history_id', string='History', readonly=True,
    #                            states={'draft': [('readonly', False)]})
    # operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit',
    #                                     readonly=True, states={'draft': [('readonly', False)]})
    # maker_id = fields.Many2one('res.users', 'Maker', default=lambda self: self.env.user.id, track_visibility='onchange')
    # approver_id = fields.Many2one('res.users', 'Checker', track_visibility='onchange')
    sou_id = fields.Many2one('sub.operating.unit', string='Sequence')
    type_tax_use = fields.Selection(default="purchase")
    operating_unit_id = fields.Many2one('operating.unit', string='Branch')

    @api.onchange('account_id')
    def _onchange_account_id(self):
        for rec in self:
            rec.sou_id = None

#     @api.one
#     def act_draft(self):
#         if self.state == 'reject':
#             self.write({
#                 'state': 'draft',
#                 'pending': True,
#                 'active': False,
#             })
#
#     @api.one
#     def act_approve(self):
#         if self.env.user.id == self.maker_id.id and self.env.user.id != SUPERUSER_ID:
#             raise ValidationError(_("[Validation Error] Maker and Approver can't be same person!"))
#         if self.state == 'draft':
#             self.write({
#                 'state': 'approve',
#                 'pending': False,
#                 'active': True,
#                 'approver_id': self.env.user.id,
#             })
#
#     @api.one
#     def act_reject(self):
#         if self.state == 'draft':
#             self.write({
#                 'state': 'reject',
#                 'pending': False,
#                 'active': False,
#             })
#
#     @api.one
#     def act_approve_pending(self):
#         if self.env.user.id == self.maker_id.id and self.env.user.id != SUPERUSER_ID:
#             raise ValidationError(_("[Validation Error] Editor and Approver can't be same person!"))
#         if self.pending == True:
#             requested = self.line_ids.search([('state', '=', 'pending'), ('line_id', '=', self.id)], order='id desc',
#                                              limit=1)
#             if requested:
#                 self.write({
#                     'name': self.name if not requested.change_name else requested.change_name,
#                     'pending': False,
#                     'active': requested.status,
#                     'approver_id': self.env.user.id,
#                 })
#                 requested.write({
#                     'state': 'approve',
#                     'change_date': fields.Datetime.now()
#                 })
#
#     @api.one
#     def act_reject_pending(self):
#         if self.pending == True:
#             requested = self.line_ids.search([('state', '=', 'pending'), ('line_id', '=', self.id)], order='id desc',
#                                              limit=1)
#             if requested:
#                 self.write({
#                     'pending': False
#                 })
#                 requested.write({
#                     'state': 'reject',
#                     'change_date': fields.Datetime.now()
#                 })
#
#     @api.multi
#     def unlink(self):
#         for rec in self:
#             if rec.state in ('approve', 'reject'):
#                 raise ValidationError(_('[Warning] Approves and Rejected record cannot be deleted.'))
#
#             try:
#                 return super(AccountTax, rec).unlink()
#             except IntegrityError:
#                 raise ValidationError(_("The operation cannot be completed, probably due to the following:\n"
#                                         "- deletion: you may be trying to delete a record while other records still reference it"))
#
#     @api.constrains('name')
#     def _check_unique_constrain(self):
#         if self.name:
#             name = self.search(
#                 [('name', '=ilike', self.name.strip()), ('state', '!=', 'reject'), '|', ('active', '=', True),
#                  ('active', '=', False)])
#             if len(name) > 1:
#                 raise Warning('[Unique Error] Name must be unique!')
#
#     @api.constrains('minimum_amount')
#     def _check_minimum_amount(self):
#         if self.minimum_amount and self.amount and self.minimum_amount >= self.amount:
#             raise Warning('Minimum Amount should be less then Rate Amount!')
#
#     @api.constrains('mushok_amount', 'vds_amount')
#     def _check_mushok_vds_amount(self):
#         if self.mushok_amount and self.amount and self.mushok_amount >= self.amount:
#             raise Warning('Mushok Amount should be less then Rate Amount!')
#         if self.vds_amount and self.amount and self.vds_amount >= self.amount:
#             raise Warning('VDS Amount should be less then Rate Amount!')
#
#     @api.onchange("name")
#     def onchange_strips(self):
#         if self.name:
#             self.name = self.name.strip()
#
#     @api.one
#     def name_get(self):
#         if self.name and self.amount:
#             name = '%s [%s]' % (self.name, self.amount)
#         return (self.id, name)
#
#
# class HistoryVAT(models.Model):
#     _name = 'history.account.tax'
#     _description = 'VAT/TDS Rule Changing History'
#     _order = 'id desc'
#
#     change_name = fields.Char('Proposed Name', size=200, readonly=True, states={'draft': [('readonly', False)]})
#     status = fields.Boolean('Active', default=True, track_visibility='onchange')
#     request_date = fields.Datetime(string='Requested Date')
#     change_date = fields.Datetime(string='Approved Date')
#     history_id = fields.Many2one('account.tax', ondelete='restrict')
#     state = fields.Selection([('pending', 'Pending'), ('approve', 'Approved'), ('reject', 'Rejected')],
#                              default='pending')
