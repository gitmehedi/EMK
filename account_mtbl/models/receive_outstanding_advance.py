from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ReceiveOutstandingAdvance(models.Model):
    _inherit = 'receive.outstanding.advance'

    debit_sub_operating_unit_id = fields.Many2one('sub.operating.unit', string='Debit Sequence', required=True,
                                                  track_visibility='onchange', readonly=True,
                                                  states={'draft': [('readonly', False)]})
    operating_unit_domain_ids = fields.Many2many('operating.unit', compute="_compute_operating_unit_domain_ids",
                                                 readonly=True, store=False)
    date = fields.Date(string='Date ', default=lambda self:self.env.user.company_id.batch_date,
                       track_visibility='onchange', readonly=True, states={'draft': [('readonly', False)]})

    @api.multi
    @api.depends('debit_sub_operating_unit_id')
    def _compute_operating_unit_domain_ids(self):
        for rec in self:
            if rec.debit_sub_operating_unit_id.all_branch:
                rec.operating_unit_domain_ids = self.env['operating.unit'].search([])
            else:
                rec.operating_unit_domain_ids = rec.debit_sub_operating_unit_id.branch_ids

    @api.onchange('debit_account_id')
    def _onchange_debit_account_id(self):
        for rec in self:
            rec.debit_sub_operating_unit_id = None

    @api.onchange('debit_sub_operating_unit_id')
    def _onchange_debit_sub_operating_unit_id(self):
        for rec in self:
            rec.debit_operating_unit_id = None

    def get_debit_item_data(self):
        res = super(ReceiveOutstandingAdvance, self).get_debit_item_data()
        if self.debit_sub_operating_unit_id:
            res['sub_operating_unit_id'] = self.debit_sub_operating_unit_id.id
        else:
            raise ValidationError('Please select Debit Sequence First')
        res['reconcile_ref'] = self.get_reconcile_ref(res['account_id'], res['ref'])
        return res

    def get_advance_credit_item(self, advance_line):
        res = super(ReceiveOutstandingAdvance, self).get_advance_credit_item(advance_line)
        if advance_line.advance_id.sub_operating_unit_id:
            res['sub_operating_unit_id'] = advance_line.advance_id.sub_operating_unit_id.id
        res['reconcile_ref'] = advance_line.advance_id.reconcile_ref
        return res

    def get_reconcile_ref(self, account_id, ref):
        # Generate reconcile ref code
        reconcile_ref = None
        account_obj = self.env['account.account'].search([('id', '=', account_id)])
        if account_obj.reconcile:
            reconcile_ref = account_obj.code + ref.replace('/', '')

        return reconcile_ref

    @api.multi
    def create_account_move(self, journal_id):
        move = super(ReceiveOutstandingAdvance, self).create_account_move(journal_id)
        move.write({
            'maker_id': self.maker_id.id,
            'approver_id': self.env.user.id
        })

        return move
