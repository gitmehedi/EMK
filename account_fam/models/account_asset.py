# -*- coding: utf-8 -*-

import calendar
from datetime import datetime, timedelta
from datetime import date as DT
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _, tools
from odoo.exceptions import ValidationError, UserError
from odoo.tools import float_compare, float_is_zero

DATE_FORMAT = "%Y-%m-%d"


class AccountAssetAsset(models.Model):
    _inherit = 'account.asset.asset'
    _order = "id DESC,allocation_status ASC"

    name = fields.Char(string='Asset Name', required=True, readonly=True, states={'close': [('readonly', False)]})
    category_id = fields.Many2one(string='Asset Type', required=True, change_default=True, readonly=True)
    asset_type_id = fields.Many2one(string='Asset Category', required=True, change_default=True, readonly=True)
    asset_seq = fields.Char(string='Asset Code', track_visibility='onchange')
    batch_no = fields.Char(string='Batch No', readonly=True,
                           track_visibility='onchange', )
    method_progress_factor = fields.Float(string='Depreciation Factor', digits=(1, 3), readonly=True, default=0.0,
                                          states={'draft': [('readonly', False)]})
    method_number = fields.Integer(string='Number of Depreciations', default=0,
                                   help="The number of depreciations needed to depreciate your asset")
    is_custom_depr = fields.Boolean(default=True, required=True, track_visibility='onchange')
    partner_id = fields.Many2one('res.partner', string="Vendor", track_visibility='onchange')
    depreciation_year = fields.Integer(string='Asset Life (In Year)', required=True, default=0, readonly=True,
                                       track_visibility='onchange', states={'draft': [('readonly', False)]})
    method = fields.Selection([('degressive', 'Reducing Method'),
                               ('linear', 'Straight Line/Linear'),
                               ('no_depreciation', 'No Depreciation')],
                              track_visibility='onchange',
                              string='Computation Method', required=True, default='degressive',
                              help="Choose the method to use to compute the amount of depreciation lines.\n"
                                   "  * Linear: Calculated on basis of: Gross Value - Salvage Value/ Useful life of the fixed asset\n"
                                   "  * Reducing Method: Calculated on basis of: Residual Value * Depreciation Factor")
    warranty_date = fields.Date(string='Warranty Date', track_visibility='onchange', readonly=True,
                                states={'draft': [('readonly', False)]})
    date = fields.Date(string='Purchase Date', track_visibility='onchange')
    asset_usage_date = fields.Date(string='Usage Date', help='Usage Date/Allocation Date', readonly=True,
                                   track_visibility='onchange', states={'draft': [('readonly', False)]})
    model_name = fields.Char(string='Model', track_visibility='onchange', readonly=True)
    operating_unit_id = fields.Many2one('operating.unit', string='Purchase Branch', required=True,
                                        track_visibility='onchange')
    invoice_date = fields.Date(related='invoice_id.date_invoice', string='Bill Date', track_visibility='onchange')
    method_period = fields.Integer(string='One Entry (In Month)', required=True, readonly=True, default=1,
                                   states={'draft': [('readonly', False)]}, track_visibility='onchange')
    value = fields.Float(string='Cost Value', track_visibility='onchange', readonly=True)
    depr_base_value = fields.Float(string='Depr. Base Value', track_visibility='onchange', readonly=True)
    value_residual = fields.Float(string='WDV', track_visibility='onchange', store=True)
    advance_amount = fields.Float(string='Adjusted Amount', track_visibility='onchange', readonly=True,
                                  states={'draft': [('readonly', False)]})
    current_branch_id = fields.Many2one('operating.unit', string='Current Branch', required=True,
                                        track_visibility='onchange')
    sub_operating_unit_id = fields.Many2one('sub.operating.unit', string='Sequence',
                                            track_visibility='onchange', readonly=True,
                                            states={'draft': [('readonly', False)]})
    accumulated_value = fields.Float(string='Accumulated Depr.', compute="_compute_accumulated_value",
                                     track_visibility='onchange', store=True)
    asset_description = fields.Text(string='Asset Description', readonly=True, states={'draft': [('readonly', False)]})
    cost_centre_id = fields.Many2one('account.analytic.account', string='Cost Centre', required=True,
                                     track_visibility='onchange', readonly=True)
    note = fields.Text(string="Note", required=False, readonly=True, states={'draft': [('readonly', False)]})
    allocation_status = fields.Boolean(string='Allocation Status', track_visibility='onchange', default=False)
    depreciation_flag = fields.Boolean(string='Awaiting Disposal', track_visibility='onchange', default=False)
    lst_depr_date = fields.Date(string='Last Depr. Date', readonly=True, track_visibility='onchange')
    lst_depr_amount = fields.Float(string='Last Depr. Amount', readonly=True, track_visibility='onchange', store=True)
    awaiting_dispose_date = fields.Date(string='Awaiting Dispose Date', readonly=True, track_visibility='onchange')
    dmc_date = fields.Date(string='DMC Date', readonly=True, track_visibility='onchange')
    end_of_date = fields.Date(string='End of Date')
    reconcile_ref = fields.Char(string='Reconcile Ref', size=20, readonly=True)
    asset_status = fields.Selection([('active', 'Active'),
                                     ('sell', 'Sell'),
                                     ('dispose', 'dispose')], default='active')

    @api.model_cr
    def init(self):
        self._cr.execute("""
            CREATE OR REPLACE FUNCTION asset_depreciation(date DATE,user_id INTEGER,journal_id INTEGER,opu_id INTEGER,company_id INTEGER, narr_date TEXT,sys_date DATE) 
                    RETURNS INTEGER AS $$
                    DECLARE
                    rec RECORD;
                    mrec RECORD;
                    query TEXT;
                    move_query TEXT;
                    move INTEGER;
                    user_id INTEGER;
                    no_days INTEGER;
                    depr_date DATE;
                    depr_amount FLOAT;
                    delta_days INTEGER;
                    delta_date DATE;
                    daily_depr FLOAT;
                    linear TEXT;
                    degr_start DATE;
                    degr_end DATE;
                    lin_start INTEGER;
                    lin_end INTEGER;
                    cumul_depr FLOAT;
                    book_val_amount FLOAT;
                    d_days INTEGER;
                    d_month INTEGER;
                    BEGIN
                    depr_date = date;
                    user_id = user_id;
                    journal_id = journal_id;
                    opu_id = opu_id;
                    company_id = company_id;
					narr_date = narr_date;
                
                    query = 'SELECT aaa.*,
                        aac.id AS category_id,
                        aac.journal_id,
                        aac.account_depreciation_id,
                        aac.account_depreciation_expense_id 
                        FROM account_asset_asset aaa
                        LEFT JOIN account_asset_category aac
                           ON (aaa.asset_type_id = aac.id)
                        WHERE  aaa.depreciation_flag=False 
                         AND aaa.allocation_status=True';
                         
                    INSERT INTO account_move (name,ref,journal_id,company_id,date,operating_unit_id,user_id,state,is_cbs,is_sync,is_cr,create_uid,write_uid,create_date,write_date) 
                        VALUES ('/','Asset Depreciation on '|| depr_date ,journal_id,company_id,sys_date,opu_id,user_id,'draft',False,False,False,user_id,user_id,sys_date,sys_date)
                        RETURNING account_move.id INTO move;
                
                    FOR rec IN EXECUTE query
                    LOOP
                
                    IF rec.lst_depr_date IS NOT NULL THEN
                      no_days := (depr_date - rec.lst_depr_date)::integer;
                    ELSE
                      no_days := (depr_date - rec.asset_usage_date)::integer;
                    END IF;
                
                    IF no_days > 0 AND rec.state='open' AND rec.method !='no_depreciation' THEN
                        IF rec.method = 'linear' THEN
                          IF rec.value_residual > 0 THEN
                              IF rec.dmc_date IS NOT NULL THEN
                                delta_days =  (rec.end_of_date -  rec.dmc_date)::integer;
								IF delta_days > 0 THEN
                                	daily_depr = rec.depr_base_value  / delta_days;
								ELSE
									daily_depr = 0;
								END IF;
                              ELSE
                                degr_start = DATE_PART('year', depr_date) || '-01-01';
                                degr_end = DATE_PART('year', depr_date) || '-12-31';
                                delta_days =  degr_end -  degr_start + 1;
                                daily_depr = (rec.depr_base_value / rec.depreciation_year) / delta_days;
                              END IF;
                          ELSE
                                daily_depr = 0;
                          END IF;
                          
                        ELSEIF rec.method = 'degressive' THEN
                          degr_start = DATE_PART('year', depr_date) || '-01-01';
                          degr_end = DATE_PART('year', depr_date) || '-12-31';
                          delta_days =  degr_end -  degr_start + 1;
                          daily_depr = (rec.depr_base_value * rec.method_progress_factor) / delta_days;
                        END IF;
                
                        depr_amount = ROUND(no_days * daily_depr::numeric,2);
                        if depr_amount > rec.value_residual THEN
                           depr_amount = rec.value_residual;
                        END IF;
                        cumul_depr = rec.accumulated_value + depr_amount;
                        book_val_amount = rec.value_residual - depr_amount;
                        
                        IF depr_amount > 0 THEN
                        -- insert data into account.move table
                        INSERT INTO account_asset_depreciation_line (move_id,asset_id,name,sequence,move_check,move_posted_check,line_type,depreciation_date,days,amount,depreciated_value,remaining_value,create_uid,write_uid,create_date,write_date)
                        VALUES (move,rec.id,'Depreciation',1,True,True,'depreciation',depr_date,no_days,depr_amount,cumul_depr,book_val_amount,user_id,user_id,NOW(),NOW());
                
                        d_days = DATE_PART('days', depr_date);
                        d_month = DATE_PART('month', depr_date);
                        IF d_days=31 AND d_month=12 AND rec.method='degressive' THEN
                            UPDATE account_asset_asset
                            SET lst_depr_date = depr_date,
                            lst_depr_amount = depr_amount,
                            accumulated_value=cumul_depr,
                            value_residual=book_val_amount,
                            depr_base_value=book_val_amount,
                            write_uid=user_id,
                            write_date=NOW()
                            WHERE id = rec.id;
                        ELSE
                            UPDATE account_asset_asset
                            SET lst_depr_date = depr_date,
                            lst_depr_amount = depr_amount,
                            accumulated_value=cumul_depr,
                            value_residual=book_val_amount,
                            write_uid=user_id,
                            write_date=NOW()
                            WHERE id = rec.id;
                        END IF;
                        END IF;
                        --RAISE NOTICE '% - %', move, move;
                    END IF;
                    END LOOP;
                    move_query='SELECT aaa.current_branch_id,
                            aaa.cost_centre_id,
							dsou.name as depr_name,
							dsou.code as depr_code,
	                        adsou.name as acc_depr_name,
	                        adsou.code as acc_depr_code,
                            aac.account_depreciation_id,
                            aac.account_depreciation_seq_id,
                            aac.account_depreciation_expense_id,
                            aac.account_depreciation_expense_seq_id,
                            SUM(aaa.lst_depr_amount) AS depr_sum
                        FROM account_asset_asset aaa
                        LEFT JOIN account_asset_category aac
                               ON (aaa.asset_type_id = aac.id)
                        LEFT JOIN account_asset_depreciation_line aadl
                               ON (aadl.asset_id = aaa.id)
                        LEFT JOIN sub_operating_unit dsou
                               ON (dsou.id = aac.account_depreciation_expense_seq_id)
                        LEFT JOIN sub_operating_unit adsou
                               ON (adsou.id = aac.account_depreciation_seq_id)
                        WHERE  aaa.depreciation_flag=False 
                             AND aaa.allocation_status=True
                             AND aadl.move_id= '|| move || 
                         'GROUP BY aaa.current_branch_id,
                            aaa.cost_centre_id,
							dsou.name,
							dsou.code,
	                        adsou.name,
	                        adsou.code,
                            aac.account_depreciation_id,
                            aac.account_depreciation_seq_id,
                            aac.account_depreciation_expense_id,
                            aac.account_depreciation_expense_seq_id
                          ORDER BY aaa.current_branch_id DESC';
                    FOR mrec IN EXECUTE move_query
                    LOOP
                          -- insert credit amount in account.move.line
                          INSERT INTO account_move_line (name,ref,journal_id,move_id,account_id,operating_unit_id,sub_operating_unit_id,analytic_account_id,date_maturity,date,debit,credit,create_uid,write_uid,create_date,write_date,is_bgl,company_id)
                          VALUES ('Depreciation on ' || mrec.depr_name || narr_date,mrec.account_depreciation_id,journal_id,move,mrec.account_depreciation_expense_id,mrec.current_branch_id,mrec.account_depreciation_expense_seq_id,mrec.cost_centre_id,sys_date,sys_date,mrec.depr_sum,0,user_id,user_id,NOW(),NOW(),'not_check',company_id);
                          -- insert debit amount in account.move.line
                          INSERT INTO account_move_line (name,ref,journal_id,move_id,account_id,operating_unit_id,sub_operating_unit_id,analytic_account_id,date_maturity,date,debit,credit,create_uid,write_uid,create_date,write_date,is_bgl,company_id)
                          VALUES ('Accu. Depr. on ' || mrec.acc_depr_name || narr_date,mrec.account_depreciation_id,journal_id,move,mrec.account_depreciation_id,mrec.current_branch_id,mrec.account_depreciation_seq_id,mrec.cost_centre_id,sys_date,sys_date,0,mrec.depr_sum,user_id,user_id,NOW(),NOW(),'not_check',company_id);
                        
                    END LOOP;
                    RETURN move;
                END;
            $$ LANGUAGE plpgsql;
        """)

    @api.model
    def create(self, vals):
        asset = super(AccountAssetAsset, self).create(vals)
        return asset

    @api.multi
    def write(self, vals):
        res = super(AccountAssetAsset, self).write(vals)
        return res

    @api.constrains('depreciation_year')
    def check_depreciation_year(self):
        if self.method == 'linear':
            if self.depreciation_year < 1:
                raise ValidationError(_('Asset Life cann\'t be zero or negative value.'))

    @api.onchange('depreciation_year')
    def onchange_depreciation_year(self):
        if self.method == 'linear':
            if self.depreciation_year:
                self.method_number = int(12 * self.depreciation_year)

    @api.multi
    @api.depends('value', 'salvage_value', 'depreciation_line_ids.move_check', 'depreciation_line_ids.amount')
    def _compute_accumulated_value(self):
        for rec in self:
            rec.accumulated_value = rec.value - rec.value_residual

    @api.onchange("name")
    def onchange_strips(self):
        if self.name:
            self.name = self.name.strip()

    @api.multi
    def validate(self):
        super(AccountAssetAsset, self).validate()

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            name = record.name
            if record.asset_seq:
                name = '[' + record.asset_seq + '] ' + record.name
            result.append((record.id, name))
        return result

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        names1 = super(models.Model, self).name_search(name=name, args=args, operator=operator, limit=limit)
        names2 = []
        if name:
            domain = [('name', '=ilike', name + '%')]
            names2 = self.search(domain, limit=limit).name_get()
        return list(set(names1) | set(names2))[:limit]

    @api.model
    def _needaction_domain_get(self):
        return [('state', 'in', ('open', 'draft'))]

    @api.multi
    def compute_depreciation_board(self):
        return False

    @api.multi
    def _get_last_depreciation_date(self):
        """
        @param id: ids of a account.asset.asset objects
        @return: Returns a dictionary of the effective dates of the last depreciation entry made for given asset ids. If there isn't any, return the purchase date of this asset
        """
        self.env.cr.execute("""
                        SELECT a.id as id, COALESCE(MAX(rel.depreciation_date),a.asset_usage_date) AS date
                        FROM account_asset_asset a
                        LEFT JOIN account_asset_depreciation_line rel ON (rel.asset_id = a.id)
                        WHERE a.id IN %s
                        GROUP BY a.id, rel.depreciation_date """, (tuple(self.ids),))
        result = dict(self.env.cr.fetchall())
        return result

    @api.model
    def _cron_generate_entries(self):
        return False

    @api.model
    def _generate_depreciation(self, date):
        journal_id = self.env.user.company_id.fa_journal_id
        if not journal_id:
            raise ValidationError(_('Configure Fixed Asset Journal from Settings.'))

        company_id = self.env.user.company_id.id
        opu_id = self.env.user.default_operating_unit_id.id
        narr_date = datetime.strptime(date, DATE_FORMAT).strftime(' - %b, %Y')
        system_date = self.env.user.company_id.batch_date
        self.env.cr.execute("""SELECT * FROM asset_depreciation('%s',%s,%s,%s,%s,'%s','%s')""" % (
            date, self.env.uid, journal_id.id, opu_id, company_id, narr_date, system_date));
        debit, credit = 0, 0
        for val in self.env.cr.fetchall():
            move = self.env['account.move'].search([('id', '=', val[0])])
            for rec in move.line_ids:
                debit = debit + rec.debit
                credit = credit + rec.credit
            if debit == credit and debit > 0 and credit > 0:
                move.write({'amount': debit})
                return move
            else:
                move.unlink()
                return False

    @api.model
    def compute_depreciation_history(self, date, asset):
        if asset.allocation_status and asset.state == 'open' and not asset.depreciation_flag and asset.asset_type_id.method != 'no_depreciation':
            if self.lst_depr_date:
                no_of_days = (date - self.date_str_format(asset.lst_depr_date)).days
            else:
                no_of_days = (date - self.date_str_format(asset.asset_usage_date)).days

            if no_of_days > 0:
                if asset.method == 'linear':
                    if asset.value_residual > 0:
                        if asset.dmc_date:
                            end_date = datetime.strptime(asset.asset_usage_date, DATE_FORMAT) + relativedelta(
                                years=asset.depreciation_year)
                            date_delta = (end_date - self.date_str_format(asset.dmc_date)).days
                            if date_delta > 0:
                                daily_depr = asset.depr_base_value / date_delta
                            else:
                                daily_depr = 0;
                        else:
                            year = date.year
                            date_delta = (DT(year, 12, 31) - DT(year, 01, 01)).days + 1
                            daily_depr = (asset.depr_base_value / asset.depreciation_year) / date_delta
                    else:
                        daily_depr = 0;

                elif asset.method == 'degressive':
                    year = date.year
                    date_delta = (DT(year, 12, 31) - DT(year, 01, 01)).days + 1
                    daily_depr = (asset.depr_base_value * asset.method_progress_factor) / date_delta

                depr_amount = no_of_days * daily_depr
                if depr_amount > asset.value_residual:
                    depr_amount = asset.value_residual

                cumul_depr = sum([rec.amount for rec in asset.depreciation_line_ids]) + depr_amount
                book_val_amount = asset.value_residual - depr_amount

                if depr_amount > 0:
                    vals = {
                        'amount': depr_amount,
                        'asset_id': self.id,
                        'sequence': 1,
                        'name': (asset.code or '') + '/' + str(1),
                        'remaining_value': abs(book_val_amount),
                        'depreciated_value': cumul_depr,
                        'depreciation_date': date.date(),
                        'days': no_of_days,
                        'asset_id': asset.id,
                    }

                    rec = asset.depreciation_line_ids.search(
                        [('asset_id', '=', vals['asset_id']), ('depreciation_date', '=', date.date())])
                    if not rec:
                        depreciation = asset.depreciation_line_ids.create(vals)
                        if depreciation:
                            move = asset.create_move(depreciation, date)
                            if date.month == 12 and date.day == 31 and asset.method == 'degressive':
                                asset.write({'lst_depr_date': date.date(),
                                             'lst_depr_amount': depr_amount,
                                             'depr_base_value': book_val_amount
                                             })
                            else:
                                asset.write({'lst_depr_date': date.date(),
                                             'lst_depr_amount': depr_amount
                                             })
                            return move

    @api.multi
    def create_move(self, line, date):
        created_moves = self.env['account.move']
        prec = self.env['decimal.precision'].precision_get('Account')
        sys_date = self.env.user.company_id.batch_date

        if line:
            if line.move_id:
                raise UserError(
                    _('This depreciation is already linked to a journal entry! Please post or delete it.'))

            category_id = line.asset_id.asset_type_id
            if not category_id.account_depreciation_id or not category_id.account_depreciation_expense_id.id:
                raise UserError(
                    _('Asset Category [{0}] need to set following fields'
                      ' \n - Depreciation Exp. A/C \n - Accumulated Depreciation A/C'.format(
                        line.asset_id.asset_type_id.name)))

            depreciation_date = self.env.context.get(
                'depreciation_date') or line.depreciation_date or fields.Date.context_today(self)
            company_currency = line.asset_id.company_id.currency_id
            current_currency = line.asset_id.currency_id
            amount = current_currency.with_context(date=depreciation_date).compute(line.amount, company_currency)

            move_line_1 = {
                'name': 'Depreciation on ' + category_id.account_depreciation_seq_id.name + date.strftime(' - %b, %Y'),
                'account_id': category_id.account_depreciation_id.id,
                'debit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
                'credit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
                'journal_id': category_id.journal_id.id if category_id.journal_id else False,
                'partner_id': line.asset_id.partner_id.id if line.asset_id.partner_id else False,
                'analytic_account_id': line.asset_id.cost_centre_id.id if line.asset_id.cost_centre_id else False,
                'operating_unit_id': line.asset_id.current_branch_id.id,
                'sub_operating_unit_id': category_id.account_depreciation_seq_id.id if category_id else False,
                'currency_id': company_currency != current_currency and current_currency.id or False,
                'amount_currency': company_currency != current_currency and - 1.0 * line.amount or 0.0,
                'date': sys_date,
                'date_maturity': sys_date,
                'company_id': self.env.user.company_id.id,
            }
            move_line_2 = {
                'name': 'Accu. Depr. on ' + category_id.account_depreciation_expense_seq_id.name + date.strftime(
                    ' - %b, %Y'),
                'account_id': category_id.account_depreciation_expense_id.id,
                'credit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
                'debit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
                'journal_id': category_id.journal_id.id if category_id.journal_id else False,
                'partner_id': line.asset_id.partner_id.id if line.asset_id.partner_id else False,
                'analytic_account_id': line.asset_id.cost_centre_id.id if line.asset_id.cost_centre_id else False,
                'operating_unit_id': line.asset_id.current_branch_id.id,
                'sub_operating_unit_id': category_id.account_depreciation_expense_seq_id.id if category_id else False,
                'currency_id': company_currency != current_currency and current_currency.id or False,
                'amount_currency': company_currency != current_currency and line.amount or 0.0,
                'date': sys_date,
                'date_maturity': sys_date,
                'company_id': self.env.user.company_id.id,
            }
            move_vals = {
                'ref': 'Asset Depreciation on {0}'.format(depreciation_date),
                'date': sys_date,
                'journal_id': category_id.journal_id.id,
                'line_ids': [(0, 0, move_line_1), (0, 0, move_line_2)],
            }
            move = self.env['account.move'].create(move_vals)
            line.write({'move_id': move.id, 'move_check': True})
            created_moves |= move

        if move.state == 'draft' and line.move_id.id == move.id:
            return move

    @api.multi
    def _compute_entries(self, date, group_entries=False):
        depreciation_ids = self.env['account.asset.depreciation.line'].search([
            ('asset_id', 'in', self.ids), ('depreciation_date', '<=', date),
            ('move_check', '=', False), ('active', '=', False)])
        if group_entries:
            return depreciation_ids.create_grouped_move()
        return depreciation_ids.create_move()

    def onchange_category_id_values(self, category_id):
        if category_id:
            category = self.env['account.asset.category'].browse(category_id)
            return {
                'value': {
                    'method': category.method,
                    'method_number': category.method_number,
                    'method_time': category.method_time,
                    'method_period': category.method_period,
                    'method_progress_factor': category.method_progress_factor,
                    'method_end': category.method_end,
                    'prorata': category.prorata,
                    'depreciation_year': category.depreciation_year,
                }
            }

    @api.multi
    def set_to_close(self, date):
        for asset in self:
            if asset.allocation_status and asset.state == 'open' and asset.depreciation_flag:
                last_depr_date = asset.lst_depr_date
                curr_depr_date = self.date_depr_format(date)

                depr_amount = asset.value_residual
                book_val_amount = asset.value_residual - depr_amount

                if last_depr_date:
                    no_of_days = (curr_depr_date - self.date_str_format(last_depr_date)).days
                else:
                    no_of_days = 0

                vals = {
                    'amount': asset.value_residual,
                    'asset_id': self.id,
                    'sequence': 1,
                    'name': (asset.code or '') + '/' + str(1),
                    'remaining_value': abs(book_val_amount),
                    'depreciated_value': asset.value_residual,
                    'depreciation_date': curr_depr_date.date(),
                    'days': no_of_days,
                    'asset_id': asset.id,
                }

                depreciation = asset.depreciation_line_ids.create(vals)
                if depreciation:
                    if asset.create_move(depreciation, date):
                        asset.write({'lst_depr_date': curr_depr_date.date(),
                                     'state': 'close'})
                        return True

    def date_depr_format(self, date):
        no_of_days = calendar.monthrange(date.year, date.month)[1]
        return date.replace(day=no_of_days)

    def date_str_format(self, date):
        if type(date) is str:
            return datetime.strptime(date, DATE_FORMAT)
        elif type(date) is datetime:
            return "{0}-{1}-{2}".format(date.year, date.month, date.day)


class AccountAssetDepreciationLine(models.Model):
    _inherit = 'account.asset.depreciation.line'

    days = fields.Integer(string='Days', required=True)
    line_type = fields.Selection([('depreciation', 'Depreciation'), ('sale', 'Sale'), ('dispose', 'Dispose')],
                                 default='depreciation', required=True, string="Line Type")
    amount = fields.Float(string='Depreciation')
    remaining_value = fields.Float(string='WDV at Date')
    depreciation_date = fields.Date('Date')

    @api.multi
    def create_move(self, post_move=True):
        self.asset_id.create_move(self)
        return self.move_check

    def format_dispose_move(self, amount, asset_name, category_id, prec, line, company_currency, current_currency,
                            depreciation_date, current_branch):
        depr_credit = {
            'name': asset_name,
            'account_id': category_id.account_asset_id.id,
            'debit': 0.0,
            'credit': self.asset_id.value if float_compare(self.asset_id.value, 0.0,
                                                           precision_digits=prec) > 0 else 0.0,
            'journal_id': category_id.journal_id.id if category_id.journal_id else False,
            'partner_id': line.asset_id.partner_id.id if line.asset_id.partner_id else False,
            'currency_id': company_currency != current_currency and current_currency.id or False,
            'amount_currency': company_currency != current_currency and - 1.0 * line.amount or 0.0,
        }
        depr_debit_1 = {
            'name': asset_name,
            'account_id': category_id.account_depreciation_id.id,
            'credit': 0.0,
            'debit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
            'journal_id': category_id.journal_id.id if category_id.journal_id else False,
            'partner_id': line.asset_id.partner_id.id if line.asset_id.partner_id else False,
            'currency_id': company_currency != current_currency and current_currency.id or False,
            'amount_currency': company_currency != current_currency and line.amount or 0.0,
        }
        depr_debit_2 = {
            'name': asset_name,
            'account_id': category_id.account_asset_loss_id.id,
            'debit': self.asset_id.value - amount if float_compare(self.asset_id.value - amount, 0.0,
                                                                   precision_digits=prec) > 0 else 0.0,
            'credit': 0.0,
            'journal_id': category_id.journal_id.id if category_id.journal_id else False,
            'partner_id': line.asset_id.partner_id.id if line.asset_id.partner_id else False,
            'currency_id': company_currency != current_currency and current_currency.id or False,
            'amount_currency': company_currency != current_currency and - 1.0 * line.amount or 0.0,
        }
        return {
            'ref': line.asset_id.code,
            'date': depreciation_date or False,
            'journal_id': category_id.journal_id.id,
            'operating_unit_id': current_branch.id,
            'line_ids': [(0, 0, depr_credit), (0, 0, depr_debit_1), (0, 0, depr_debit_2)],
        }

    def format_sale_move(self, amount, asset_name, category_id, prec, line, company_currency, current_currency,
                         depreciation_date, current_branch):
        sale_id = self.env['account.asset.sale'].search([('name', '=', self.env.context.get('sale_id'))])
        sales = self.env['account.asset.sale.line'].search(
            [('sale_id', '=', sale_id.id), ('asset_id', '=', self.asset_id.id)])

        if sales.sale_value > amount:
            gain = sales.sale_value - amount
            loss_gain = {
                'name': asset_name,
                'account_id': category_id.account_asset_gain_id.id,
                'debit': 0.0,
                'credit': gain if float_compare(gain, 0.0, precision_digits=prec) > 0 else 0.0,
                'journal_id': category_id.journal_id.id if category_id.journal_id else False,
                'partner_id': line.asset_id.partner_id.id if line.asset_id.partner_id else False,
                'currency_id': company_currency != current_currency and current_currency.id or False,
                'amount_currency': company_currency != current_currency and - 1.0 * line.amount or 0.0,
            }
        else:
            loss = amount - sales.sale_value
            loss_gain = {
                'name': asset_name,
                'account_id': category_id.account_asset_loss_id.id,
                'debit': loss if float_compare(loss, 0.0, precision_digits=prec) > 0 else 0.0,
                'credit': 0.0,
                'journal_id': category_id.journal_id.id if category_id.journal_id else False,
                'partner_id': line.asset_id.partner_id.id if line.asset_id.partner_id else False,
                'currency_id': company_currency != current_currency and current_currency.id or False,
                'amount_currency': company_currency != current_currency and - 1.0 * line.amount or 0.0,
            }
        asset_credit = {
            'name': asset_name,
            'account_id': category_id.account_asset_id.id,
            'debit': 0.0,
            'credit': self.asset_id.value if float_compare(self.asset_id.value, 0.0,
                                                           precision_digits=prec) > 0 else 0.0,
            'journal_id': category_id.journal_id.id if category_id.journal_id else False,
            'partner_id': line.asset_id.partner_id.id if line.asset_id.partner_id else False,
            'currency_id': company_currency != current_currency and current_currency.id or False,
            'amount_currency': company_currency != current_currency and - 1.0 * line.amount or 0.0,
        }
        depr_debit = {
            'name': asset_name,
            'account_id': category_id.account_depreciation_id.id,
            'credit': 0.0,
            'debit': self.asset_id.value - amount if float_compare(self.asset_id.value - amount, 0.0,
                                                                   precision_digits=prec) > 0 else 0.0,
            'journal_id': category_id.journal_id.id if category_id.journal_id else False,
            'partner_id': line.asset_id.partner_id.id if line.asset_id.partner_id else False,
            'currency_id': company_currency != current_currency and current_currency.id or False,
            'amount_currency': company_currency != current_currency and line.amount or 0.0,
        }

        sale_susp_debit = {
            'name': asset_name,
            'account_id': category_id.asset_sale_suspense_account_id.id,
            'debit': sales.sale_value if float_compare(sales.sale_value, 0.0, precision_digits=prec) > 0 else 0.0,
            'credit': 0.0,
            'journal_id': category_id.journal_id.id if category_id.journal_id else False,
            'partner_id': line.asset_id.partner_id.id if line.asset_id.partner_id else False,
            'currency_id': company_currency != current_currency and current_currency.id or False,
            'amount_currency': company_currency != current_currency and - 1.0 * line.amount or 0.0,
        }
        return {
            'ref': line.asset_id.code,
            'date': depreciation_date or False,
            'journal_id': category_id.journal_id.id,
            'operating_unit_id': current_branch.id,
            'line_ids': [(0, 0, asset_credit), (0, 0, depr_debit), (0, 0, loss_gain), (0, 0, sale_susp_debit)],
        }

    def format_depreciation_move(self, amount, asset_name, category_id, prec, line, company_currency,
                                 current_currency, depreciation_date, current_branch):
        move_line_1 = {
            'name': asset_name,
            'account_id': category_id.account_depreciation_id.id,
            'debit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
            'credit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
            'journal_id': category_id.journal_id.id if category_id.journal_id else False,
            'partner_id': line.asset_id.partner_id.id if line.asset_id.partner_id else False,
            'currency_id': company_currency != current_currency and current_currency.id or False,
            'amount_currency': company_currency != current_currency and - 1.0 * line.amount or 0.0,
        }
        move_line_2 = {
            'name': asset_name,
            'account_id': category_id.account_depreciation_expense_id.id,
            'credit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
            'debit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
            'journal_id': category_id.journal_id.id if category_id.journal_id else False,
            'partner_id': line.asset_id.partner_id.id if line.asset_id.partner_id else False,
            'currency_id': company_currency != current_currency and current_currency.id or False,
            'amount_currency': company_currency != current_currency and line.amount or 0.0,
        }
        return {
            'ref': line.asset_id.code,
            'date': depreciation_date or False,
            'journal_id': category_id.journal_id.id,
            'operating_unit_id': current_branch.id,
            'line_ids': [(0, 0, move_line_1), (0, 0, move_line_2)],
        }

    @api.multi
    def post_lines_and_close_asset(self):
        # Overwrite this function because it's create a new entry every time
        return True
