from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import ValidationError

DATE_FORMAT = "%Y-%m-%d"


class TPMProductChangeRequest(models.Model):
    _name = 'tpm.product.change.request'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'TPM Product Rate Change'
    _order = 'id desc'
    _depreciation = []

    def _get_income_rate(self):
        tpm_config = self.env['res.tpm.config.settings'].search([], order='id desc', limit=1)
        if not tpm_config:
            raise Warning(_("Please configure proper settings for TPM"))
        return tpm_config.income_rate

    def _get_expense_rate(self):
        tpm_config = self.env['res.tpm.config.settings'].search([], order='id desc', limit=1)
        if not tpm_config:
            raise Warning(_("Please configure proper settings for TPM"))
        return tpm_config.expense_rate

    @api.model
    def _get_local_account(self):
        currency = self.env.user.company_id.currency_id.id
        query = """SELECT id,name,code FROM account_account 
                    WHERE level_id=6 AND code ~ '^[1234].*' 
                          AND tpm_currency_id=%s
                    ORDER BY code DESC;""" % currency
        self.env.cr.execute(query)
        ids = [val[2] for val in self.env.cr.fetchall()]
        return [('code', 'in', tuple(ids))]

    @api.model
    def _get_fc_account(self):
        currency = self.env.user.company_id.currency_id.id
        query = """SELECT id,name,code FROM account_account 
                    WHERE level_id=6 AND code ~ '^[1234].*' 
                          AND tpm_currency_id!=%s
                    ORDER BY code DESC;""" % currency
        self.env.cr.execute(query)
        ids = [val[2] for val in self.env.cr.fetchall()]
        return [('code', 'in', tuple(ids))]

    @api.model
    def _get_branch(self):
        all_branch = self.env['operating.unit'].search([])
        settings = self.env['res.tpm.config.settings'].search([], order='id desc', limit=1)
        branch = all_branch - settings.excl_br_ids
        return [('id', 'in', tuple(branch.ids))]

    name = fields.Char(string='Serial No', readonly=True, default='New', track_visibility='onchange')
    branch_ids = fields.Many2many('operating.unit', string='Branch', required=True, readonly=True,
                                  domain=lambda self: self._get_branch(),
                                  track_visibility='onchange', states={'draft': [('readonly', False)]})
    account_ids = fields.Many2many('account.account', 'tpm_account_rel', 'tpm_id', 'account_id',
                                   string='Chart of Account', readonly=True,
                                   track_visibility='onchange', states={'draft': [('readonly', False)]},
                                   domain=lambda self: self._get_local_account())
    account_fc_ids = fields.Many2many('account.account', 'tpm_account_fc_rel', 'tpm_id', 'account_id',
                                      string='Chart of Account', readonly=True,
                                      track_visibility='onchange', states={'draft': [('readonly', False)]},
                                      domain=lambda self: self._get_fc_account())
    narration = fields.Char('Narration', readonly=True, size=50, track_visibility='onchange',
                            states={'draft': [('readonly', False)]})
    income_rate = fields.Float('Income Rate', required=True, default=_get_income_rate, track_visibility='onchange',
                               readonly=True, states={'draft': [('readonly', False)]})
    expense_rate = fields.Float('Expense Rate', required=True, default=_get_expense_rate, track_visibility='onchange',
                                readonly=True, states={'draft': [('readonly', False)]})
    date = fields.Date('Date', readonly=True, track_visibility='onchange', default=fields.Date.today, required=True,
                       states={'draft': [('readonly', False)]})
    narration = fields.Text('Narration', readonly=True, track_visibility='onchange', required=True,
                            states={'draft': [('readonly', False)]})
    count = fields.Char(string='Total Products')
    currency_id = fields.Selection([('lc', 'Local Currency'), ('fc', 'Foreign Currency')],
                                   string='Currency', required=True, track_visibility='onchange', default='lc',
                                   readonly=True, states={'draft': [('readonly', False)]})
    maker_id = fields.Many2one('res.users', 'Maker', default=lambda self: self.env.user, track_visibility='onchange')
    approver_id = fields.Many2one('res.users', 'Checker', track_visibility='onchange')
    approve_date = fields.Datetime('Approve Date', track_visibility='onchange')
    state = fields.Selection([('draft', "Draft"),
                              ('confirm', "Confirmed"),
                              ('approve', "Approved"),
                              ('cancel', "Canceled")], default='draft', string="Status",
                             track_visibility='onchange')

    @api.one
    def action_cancel(self):
        if self.state == 'confirm':
            self.write({
                'state': 'draft',
                'maker_id': None,
            })

    @api.one
    def action_confirm(self):
        if self.state == 'draft':
            self.write({
                'state': 'confirm',
                'maker_id': self.env.user.id,
            })

    @api.one
    def action_approve(self):
        if self.state == 'confirm':
            if self.env.user.id == self.maker_id.id and self.env.user.id != SUPERUSER_ID:
                raise ValidationError(_("[Validation Error] Maker and Approver can't be same person!"))

            for branch in self.branch_ids:
                exist_branch = self.env['res.tpm.product'].search([('branch_id', '=', branch.id)])
                if not exist_branch:
                    exist_branch = self.env['res.tpm.product'].create({'branch_id': branch.id,
                                                                       'date': self.date,
                                                                       'state': 'draft'})

                if self.currency_id == 'lc':
                    line_account_ids = dict([(val.account_id.id, val.id) for val in exist_branch.line_ids])

                    insert = ''
                    ex_ids = []
                    for rec in self.account_ids:
                        datetime = fields.Datetime.now()
                        user_id = self.env.user.id
                        line = exist_branch.id

                        if rec.id not in line_account_ids.keys():
                            insert += "({0},{1},{2},'{3}',{4},{5},{6},{7},'{8}','{9}'),".format(rec.id,
                                                                                                self.income_rate,
                                                                                                self.expense_rate,
                                                                                                self.date, line,
                                                                                                rec.tpm_currency_id.id,
                                                                                                user_id, user_id,
                                                                                                datetime, datetime)
                        else:
                            ex_ids.append(line_account_ids[rec.id])

                    if insert:
                        insert_query = """INSERT INTO res_tpm_product_line 
                                        (account_id,income_rate,expense_rate,date,line_id,currency_id,create_uid,write_uid,create_date,write_date)  
                                        VALUES %s""" % insert[:-1]

                        self.env.cr.execute(insert_query)

                    if len(ex_ids) > 0:
                        ex_str = ','.join(map(str, ex_ids))
                        update_query = """UPDATE res_tpm_product_line 
                                         SET date='%s',income_rate=%s,expense_rate=%s 
                                         WHERE id IN (%s)""" % (
                            self.date, self.income_rate, self.expense_rate, ex_str)
                        self.env.cr.execute(update_query)
                else:
                    line_account_ids = dict([(val.account_id.id, val.id) for val in exist_branch.line_fc_ids])

                    insert = ''
                    ex_ids = []
                    for rec in self.account_fc_ids:
                        datetime = fields.Datetime.now()
                        user_id = self.env.user.id
                        line = exist_branch.id

                        if rec.id not in line_account_ids.keys():
                            insert += "({0},{1},{2},'{3}',{4},{5},{6},{7},'{8}','{9}'),".format(rec.id,
                                                                                                self.income_rate,
                                                                                                self.expense_rate,
                                                                                                self.date, line,
                                                                                                rec.tpm_currency_id.id,
                                                                                                user_id, user_id,
                                                                                                datetime, datetime)
                        else:
                            ex_ids.append(line_account_ids[rec.id])

                    if insert:
                        insert_query = """INSERT INTO res_tpm_product_fc_line 
                                        (account_id,income_rate,expense_rate,date,line_id,currency_id,create_uid,write_uid,create_date,write_date)  
                                        VALUES %s""" % insert[:-1]

                        self.env.cr.execute(insert_query)

                    if len(ex_ids) > 0:
                        ex_str = ','.join(map(str, ex_ids))
                        update_query = """UPDATE res_tpm_product_fc_line 
                                         SET date='%s',income_rate=%s,expense_rate=%s 
                                         WHERE id IN (%s)""" % (
                            self.date, self.income_rate, self.expense_rate, ex_str)
                        self.env.cr.execute(update_query)

                exist_branch.write({'state': 'confirm'})

        if self.currency_id == 'fc':
            self.account_fc_ids = []
        else:
            self.account_ids = []

        self.write({
            'state': 'approve',
            'name': self.env['ir.sequence'].next_by_code('tpm.product.change.request.code') or _('New'),
            'approver_id': self.env.user.id,
            'approve_date': self.env.user.company_id.batch_date
        })

    @api.model
    def _needaction_domain_get(self):
        return [('state', '=', 'confirm')]

    # @api.multi
    # def open_entries(self):
    #     move_ids = self.env['account.asset.asset'].search(
    #         [('asset_type_id', '=', self.asset_cat_id.id), ('allocation_status', '=', True)]).ids
    #     return {
    #         'name': _(self.asset_cat_id.name),
    #         'view_type': 'form',
    #         'view_mode': 'tree,form',
    #         'res_model': 'account.asset.asset',
    #         'view_id': False,
    #         'type': 'ir.actions.act_window',
    #         'domain': [('id', 'in', move_ids)],
    #     }

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state in ('approve', 'confirm'):
                raise ValidationError(_('[Warning] Approved and Confirm Record cannot deleted.'))
        return super(TPMProductChangeRequest, self).unlink()
