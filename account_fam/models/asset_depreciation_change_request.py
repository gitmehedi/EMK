from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import ValidationError
from odoo.tools import float_compare

DATE_FORMAT = "%Y-%m-%d"


class AssetDepreciationChangeRequest(models.Model):
    _name = 'asset.depreciation.change.request'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Depreciation Method Change'
    _order = 'id desc'
    _depreciation = []

    def _get_depr_date(self):
        history = self.env['account.asset.depreciation.history'].search([], order='date desc', limit=1)
        if history:
            date = history.date
        else:
            date = self.env['res.company'].search([('id', '=', self.env.user.id)], limit=1).batch_date
        return date

    name = fields.Char(required=False, track_visibility='onchange', string='Name')
    asset_life = fields.Integer('Asset Life (In Year)', required=True, readonly=True,
                                states={'draft': [('readonly', False)]})
    narration = fields.Char('Narration', readonly=True, size=50, required=True, states={'draft': [('readonly', False)]})
    method_progress_factor = fields.Float('Depreciation Factor', readonly=True, states={'draft': [('readonly', False)]})

    change_date = fields.Date('Change Date', readonly=True, states={'draft': [('readonly', False)]})
    request_date = fields.Date('Date', default=_get_depr_date, required=True,
                               readonly=True, states={'draft': [('readonly', False)]})
    approve_date = fields.Date('Approved Date', readonly=True, states={'draft': [('readonly', False)]})
    asset_type_id = fields.Many2one('account.asset.category', track_visibility='onchange', required=True,
                                    domain=[('parent_id', '=', False)],
                                    string='Asset Type', readonly=True,
                                    states={'draft': [('readonly', False)]})
    asset_cat_id = fields.Many2one('account.asset.category', track_visibility='onchange', required=True,
                                   domain=[('parent_id', '!=', False), ('method', '=', 'degressive')],
                                   string='Asset Category', readonly=True,
                                   states={'draft': [('readonly', False)]})
    method = fields.Selection([('linear', 'Straight Line/Linear')], default='linear', string="Computation Method",
                              track_visibility='onchange', readonly=True, states={'draft': [('readonly', False)]})
    maker_id = fields.Many2one('res.users', 'Maker', default=lambda self: self.env.user.id, track_visibility='onchange')
    approver_id = fields.Many2one('res.users', 'Checker', track_visibility='onchange')
    move_id = fields.Many2one('account.move', string='Journal', track_visibility='onchange', readonly=True)
    line_ids = fields.One2many('asset.depreciation.change.request.line', 'line_id', track_visibility='onchange',
                               readonly=True, states={'draft': [('readonly', False)]})
    asset_count = fields.Char(compute='_count_asset', store=True, string='No of Assets')

    state = fields.Selection([
        ('draft', "Draft"),
        ('confirm', "Confirmed"),
        ('approve', "Approved"),
        ('cancel', "Canceled")], default='draft', string="Status",
        track_visibility='onchange')

    @api.model_cr
    def init(self):
        self._cr.execute("""
                CREATE OR REPLACE FUNCTION ASSET_DEPRECIATION_METHOD_CHANGE(CATEGORY_ID INTEGER,DM_DATE DATE,ASSET_LIFE INTEGER,DEPR_METHOD TEXT,NARRATION TEXT, SYS_DATE DATE,USER_ID INTEGER,COMPANY_ID INTEGER,OPU_ID INTEGER,JOURNAL_ID INTEGER,ACC_DEPR INTEGER,ACC_DEPR_SEQ INTEGER,ACC_DEPR_EXP INTEGER,ACC_DEPR_EXP_SEQ INTEGER) RETURNS INTEGER AS $$
                    DECLARE
					assets TEXT;
                    asset RECORD;
                    mrec RECORD;
					usage_date DATE;
					move INTEGER;
					depreciated_amount FLOAT;
					remaining_value FLOAT;
					no_days INTEGER;
					duration TEXT;
                    BEGIN
                  
                    assets = 'SELECT *
								FROM ACCOUNT_ASSET_ASSET
								WHERE ASSET_TYPE_ID = '|| CATEGORY_ID;

                    INSERT INTO account_move (name,ref,journal_id,company_id,date,operating_unit_id,user_id,state,is_cbs,is_sync,is_cr,create_uid,write_uid,create_date,write_date)
                        VALUES ('/',NARRATION ,JOURNAL_ID,COMPANY_ID,DM_DATE,OPU_ID,USER_ID,'draft',False,False,False,USER_ID,USER_ID,SYS_DATE,SYS_DATE)
                        RETURNING account_move.id INTO move;

                    FOR asset IN EXECUTE assets
                    LOOP
					
					IF asset.asset_usage_date IS NOT NULL THEN
         				usage_date = asset.asset_usage_date + ASSET_LIFE * INTERVAL '1 year';
						IF DM_DATE > usage_date THEN
							IF asset.state = 'open' AND asset.depreciation_flag = False THEN
								IF asset.value_residual > 0 and asset.allocation_status = True THEN
									depreciated_amount = asset.accumulated_value + asset.value_residual;
                					remaining_value = abs(asset.value - depreciated_amount);
									no_days = 0;
									
									INSERT INTO account_asset_depreciation_line (move_id,asset_id,name,sequence,move_check,move_posted_check,line_type,depreciation_date,days,amount,depreciated_value,remaining_value,create_uid,write_uid,create_date,write_date)
										VALUES (move,asset.id,'Depreciation',1,True,True,'depreciation',DM_DATE,no_days,asset.value_residual,depreciated_amount,remaining_value,USER_ID,USER_ID,NOW(),NOW());

									-- insert credit amount in account.move.line
									INSERT INTO account_move_line (name,ref,journal_id,move_id,account_id,operating_unit_id,sub_operating_unit_id,analytic_account_id,date_maturity,date,debit,credit,create_uid,write_uid,create_date,write_date,is_bgl,company_id)
									VALUES (NARRATION,ACC_DEPR,JOURNAL_ID,move,ACC_DEPR_EXP,asset.current_branch_id,ACC_DEPR_EXP_SEQ,asset.cost_centre_id,DM_DATE,DM_DATE,asset.value_residual,0,USER_ID,USER_ID,NOW(),NOW(),'not_check',COMPANY_ID);
									-- insert debit amount in account.move.line
									INSERT INTO account_move_line (name,ref,journal_id,move_id,account_id,operating_unit_id,sub_operating_unit_id,analytic_account_id,date_maturity,date,debit,credit,create_uid,write_uid,create_date,write_date,is_bgl,company_id)
									VALUES (NARRATION,ACC_DEPR,JOURNAL_ID,move,ACC_DEPR,asset.current_branch_id,ACC_DEPR_SEQ,asset.cost_centre_id,DM_DATE,DM_DATE,0,asset.value_residual,USER_ID,USER_ID,NOW(),NOW(),'not_check',COMPANY_ID);

									UPDATE account_asset_asset
									SET method = DEPR_METHOD,
										depreciation_year = ASSET_LIFE,
										method_progress_factor=0.0,
										dmc_date = DM_DATE,
										lst_depr_date = DM_DATE,
										lst_depr_amount = asset.value_residual,
										accumulated_value = asset.accumulated_value + asset.value_residual,
										value_residual = 0.0,
										state='open'
									WHERE id = asset.id;
								END IF;
							END IF;
						ELSE
							UPDATE account_asset_asset
							SET method = DEPR_METHOD,
								depreciation_year = ASSET_LIFE,
								method_progress_factor=0.0,
								dmc_date = DM_DATE,
								lst_depr_date = DM_DATE,
								end_of_date = usage_date,
								depr_base_value = asset.value_residual
							WHERE id = asset.id;
						END IF;
					ELSE
						UPDATE account_asset_asset
						SET method = DEPR_METHOD,
							depreciation_year = ASSET_LIFE,
							method_progress_factor=0.0
						WHERE id = asset.id;
					END IF;
				END LOOP;
				RETURN move;
                END;
            $$ LANGUAGE PLPGSQL;
            """)

    @api.onchange('asset_type_id')
    def onchange_asset_type_id(self):
        res = {}
        self.asset_cat_id = None
        category = self.env['account.asset.category'].search(
            [('parent_id', '=', self.asset_type_id.id), ('method', '!=', 'no_depreciation')])
        ids = category.ids if self.asset_type_id else []
        res['domain'] = {
            'asset_cat_id': [('id', 'in', ids)],
        }
        return res

    @api.constrains('asset_life', 'request_date')
    def check_asset_life(self):
        if self.asset_life < 1:
            raise ValidationError(_('Asset life should be a valid value.'))

        if self._get_depr_date() != self.request_date:
            raise ValidationError(_('Depreciation method change date must be last depreciation date.'))

    @api.depends('asset_cat_id')
    def _count_asset(self):
        for val in self:
            if val.asset_cat_id:
                asset = self.env['account.asset.asset'].search(
                    [('asset_type_id', '=', val.asset_cat_id.id), ('allocation_status', '=', True)])
                val.asset_count = len(asset.ids)

    @api.constrains('asset_cat_id', 'method')
    def check_asset_cat_id(self):
        if self.asset_cat_id.method == self.method:
            raise ValidationError(_('Asset Category current method and change request method should not be same.'))

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

            if not self.name:
                name = self.env['ir.sequence'].sudo().next_by_code('asset.depreciation.change.request')
                name = name.replace('CAT', self.asset_cat_id.code)

            category = self.env['account.asset.category'].search([('id', '=', self.asset_cat_id.id)])
            if category:
                history = self.env['history.account.asset.category'].create({'method': self.method,
                                                                             'depreciation_year': self.asset_life,
                                                                             'method_progress_factor': 0.0,
                                                                             'request_date': self.env.user.company_id.batch_date,
                                                                             'line_id': category.id,
                                                                             })
                category.write({'pending': True, 'maker_id': self.maker_id.id})
                category.act_approve_pending()

            journal_id = self.env.user.company_id.fa_journal_id
            if not journal_id:
                raise ValidationError(_('Configure Fixed Asset Journal from Settings.'))

            company_id = self.env.user.company_id.id
            opu_id = self.env.user.default_operating_unit_id.id
            system_date = self.env.user.company_id.batch_date
            acc_depr = category.account_depreciation_id.id
            acc_depr_seq = category.account_depreciation_seq_id.id
            acc_depr_exp = category.account_depreciation_expense_id.id
            acc_depr_exp_seq = category.account_depreciation_expense_seq_id.id

            self.env.cr.execute(
                """SELECT * FROM ASSET_DEPRECIATION_METHOD_CHANGE(%s,'%s',%s,'%s','%s','%s',%s,%s,%s,%s,%s,%s,%s,%s)""" % (
                    self.asset_cat_id.id, self.request_date, self.asset_life, self.method, self.narration, system_date,
                    self.env.uid, company_id, opu_id, journal_id.id, acc_depr, acc_depr_seq, acc_depr_exp,
                    acc_depr_exp_seq));

            debit, credit = 0, 0
            for val in self.env.cr.fetchall():
                move = self.env['account.move'].search([('id', '=', val[0])])
                for rec in move.line_ids:
                    debit = debit + rec.debit
                    credit = credit + rec.credit
                if debit == credit and debit > 0 and credit > 0:
                    move.write({'amount': debit})
                    if move.state == 'draft':
                        move.sudo().post()
                        self.write({'move_id': move.id if move else []})
                else:
                    move.unlink()

                self.write({
                    'state': 'approve',
                    'name': name,
                    'approver_id': self.env.user.id,
                    'approve_date': self.env.user.company_id.batch_date
                })

    @api.model
    def _needaction_domain_get(self):
        return [('state', '=', 'confirm')]

    @api.multi
    def open_entries(self):
        move_ids = self.env['account.asset.asset'].search(
            [('asset_type_id', '=', self.asset_cat_id.id), ('allocation_status', '=', True)]).ids
        return {
            'name': _(self.asset_cat_id.name),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.asset.asset',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', move_ids)],
        }

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state in ('approve', 'confirm'):
                raise ValidationError(_('[Warning] Approved and Confirm Record cannot deleted.'))
        return super(AssetDepreciationChangeRequest, self).unlink()


class AssetDepreciationChangeRequestLine(models.Model):
    _name = 'asset.depreciation.change.request.line'

    asset_id = fields.Many2one('account.asset.asset', string='Asset Name', required=True)
    line_id = fields.Many2one('asset.depreciation.change.request')
