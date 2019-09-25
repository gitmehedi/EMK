# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning
from datetime import datetime
from odoo.tools import float_compare, float_is_zero

DATE_FORMAT = "%Y-%m-%d"


class AccountAssetSale(models.Model):
    _name = 'account.asset.sale'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'name desc,id desc'
    _rec_name = 'name'

    name = fields.Char(string='Serial No', readonly=True, default='New', track_visibility='onchange')
    total_value = fields.Float(string='Cost Value', compute='_compute_total_value', track_visibility='onchange')
    total_sale_amount = fields.Float(string='Sale Value', compute='_compute_total_sale_amount',
                                     track_visibility='onchange')
    request_date = fields.Datetime(string='Request Date', required=True, default=fields.Datetime.now,
                                   readonly=True, states={'draft': [('readonly', False)]}, track_visibility='onchange')
    approve_date = fields.Datetime(string='Approve Date', readonly=True, states={'draft': [('readonly', False)]},
                                   track_visibility='onchange')
    sale_date = fields.Datetime(string='Dispose Date', readonly=True, states={'approve': [('readonly', False)]},
                                track_visibility='onchange')
    request_user_id = fields.Many2one('res.users', string='Request User', readonly=True,
                                      states={'draft': [('readonly', False)]}, default=lambda self: self.env.user,
                                      track_visibility='onchange')
    approve_user_id = fields.Many2one('res.users', string='Approve User', readonly=True,
                                      states={'draft': [('readonly', False)]}, track_visibility='onchange')
    sale_user_id = fields.Many2one('res.users', string='Dispose User', readonly=True,
                                   states={'approve': [('readonly', False)]}, track_visibility='onchange')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id.id)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, readonly=True,
                                  states={'draft': [('readonly', False)]},
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    note = fields.Text(string='Note', readonly=True, states={'draft': [('readonly', False)]},
                       track_visibility='onchange')

    line_ids = fields.One2many('account.asset.sale.line', 'sale_id', string='Sale Line', readonly=True,
                               states={'draft': [('readonly', False)]}, track_visibility='onchange')
    state = fields.Selection([('draft', 'Draft'), ('approve', 'Approved'), ('sale', 'Sold')], default='draft',
                             string='State', track_visibility='onchange')

    @api.depends('line_ids')
    def _compute_total_value(self):
        for rec in self:
            rec.total_value = sum(rec.cost_value for rec in rec.line_ids)

    @api.depends('line_ids')
    def _compute_total_sale_amount(self):
        for rec in self:
            rec.total_sale_amount = sum(rec.sale_value for rec in rec.line_ids)

    @api.one
    def action_approve(self):
        if len(self.line_ids) <= 0:
            raise Warning(_("[Warning] Sale List should not be empty."))

        if self.state == 'draft':
            self.state = 'approve'
            self.approve_date = fields.Datetime.now()
            self.approve_user_id = self.env.user.id
            self.name = self.env['ir.sequence'].next_by_code('account.asset.sale') or _('New')

    @api.one
    def action_sale(self):
        if self.state == 'approve':
            for rec in self.line_ids:
                date = datetime.strptime(fields.Datetime.now()[:10], DATE_FORMAT)
                sell = self.generate_move(rec.asset_id, rec)
                if sell.state == 'draft':
                    sell.post()
                    rec.write({'journal_entry': 'post', 'move_id': sell.id})
                    response = rec.asset_id.set_to_close(date)

            self.state = 'sale'
            self.sale_date = fields.Datetime.now()
            self.sale_user_id = self.env.user.id

    def generate_move(self, asset, rec):
        prec = self.env['decimal.precision'].precision_get('Account')
        company_currency = asset.company_id.currency_id
        current_currency = asset.currency_id

        credit = {
            'name': asset.display_name,
            'account_id': asset.asset_type_id.account_asset_id.id,
            'credit': asset.value if float_compare(asset.value, 0.0, precision_digits=prec) > 0 else 0.0,
            'debit': 0.0,
            'journal_id': asset.asset_type_id.journal_id.id,
            'operating_unit_id': asset.current_branch_id.id,
            'sub_operating_unit_id': asset.sub_operating_unit_id.id if asset.sub_operating_unit_id else None,
            'analytic_account_id': asset.cost_centre_id.id if asset.cost_centre_id else None,
            'currency_id': company_currency != current_currency and current_currency.id or False,
        }

        debit = {
            'name': asset.display_name,
            'account_id': asset.asset_type_id.account_depreciation_id.id,
            'credit': 0.0,
            'debit': float("{0:.2f}".format(asset.accumulated_value)) if float_compare(asset.accumulated_value, 0.0,
                                                              precision_digits=prec) > 0 else 0.0,
            'journal_id': asset.asset_type_id.journal_id.id,
            'operating_unit_id': asset.current_branch_id.id,
            'sub_operating_unit_id': asset.sub_operating_unit_id.id if asset.sub_operating_unit_id else None,
            'analytic_account_id': asset.cost_centre_id.id if asset.cost_centre_id else None,
            'currency_id': company_currency != current_currency and current_currency.id or False,
        }

        lg_value = rec.sale_value - rec.asset_value
        if lg_value > 0:
            lg_value = abs(lg_value)
            lg_journal = {
                'name': asset.display_name,
                'account_id': asset.asset_type_id.account_asset_gain_id.id,
                'credit': lg_value if float_compare(lg_value, 0.0, precision_digits=prec) > 0 else 0.0,
                'debit': 0.0,
                'journal_id': asset.asset_type_id.journal_id.id,
                'operating_unit_id': asset.current_branch_id.id,
                'sub_operating_unit_id': asset.sub_operating_unit_id.id if asset.sub_operating_unit_id else None,
                'analytic_account_id': asset.cost_centre_id.id if asset.cost_centre_id else None,
                'currency_id': company_currency != current_currency and current_currency.id or False,
            }
        else:
            lg_value = abs(lg_value)
            lg_journal = {
                'name': asset.display_name,
                'account_id': asset.asset_type_id.account_asset_loss_id.id,
                'credit': 0.0,
                'debit': lg_value if float_compare(lg_value, 0.0, precision_digits=prec) > 0 else 0.0,
                'journal_id': asset.asset_type_id.journal_id.id,
                'operating_unit_id': asset.current_branch_id.id,
                'sub_operating_unit_id': asset.sub_operating_unit_id.id if asset.sub_operating_unit_id else None,
                'analytic_account_id': asset.cost_centre_id.id if asset.cost_centre_id else None,
                'currency_id': company_currency != current_currency and current_currency.id or False,
            }

        debit3 = {
            'name': asset.display_name,
            'account_id': asset.asset_type_id.asset_sale_suspense_account_id.id,
            'credit': 0.0,
            'debit': rec.sale_value if float_compare(rec.sale_value, 0.0,
                                                           precision_digits=prec) > 0 else 0.0,
            'journal_id': asset.asset_type_id.journal_id.id,
            'operating_unit_id': asset.current_branch_id.id,
            'sub_operating_unit_id': asset.sub_operating_unit_id.id if asset.sub_operating_unit_id else None,
            'analytic_account_id': asset.cost_centre_id.id if asset.cost_centre_id else None,
            'currency_id': company_currency != current_currency and current_currency.id or False,
        }

        return self.env['account.move'].create({
            'ref': asset.code,
            'date': fields.Datetime.now() or False,
            'journal_id': asset.category_id.journal_id.id,
            'operating_unit_id': asset.current_branch_id.id,
            'sub_operating_unit_id': asset.sub_operating_unit_id.id,
            'line_ids': [(0, 0, credit), (0, 0, debit), (0, 0, lg_journal), (0, 0, debit3)],
        })

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state in ('approve', 'sale'):
                raise Warning(_('[Warning] Approved and Disposed Record cannot deleted.'))
        return super(AccountAssetSale, self).unlink()

    @api.model
    def _needaction_domain_get(self):
        return [('state', '=', 'approve')]


class AccountAssetSaleLine(models.Model):
    _name = 'account.asset.sale.line'
    _rec = 'id ASC'

    asset_id = fields.Many2one('account.asset.asset', required=True, string='Asset Name', domain=[''])
    cost_value = fields.Float(related='asset_id.value', string='Cost Value', required=True, digits=(14, 2))
    asset_value = fields.Float(string='WDV', required=True, digits=(14, 2))
    depreciation_value = fields.Float(string='Accumulated Depr.', required=True, digits=(14, 2))
    sale_value = fields.Float(string='Sale Value', required=True, digits=(14, 2))

    sale_id = fields.Many2one('account.asset.sale', string='Sale', ondelete='restrict')
    journal_entry = fields.Selection([('unpost', 'Unposted'), ('post', 'Posted')], default='unpost', requried=True)
    move_id = fields.Many2one('account.move', string='Journal')

    @api.onchange('asset_id')
    def onchange_asset(self):
        if self.asset_id:
            self.asset_value = self.asset_id.value_residual
            self.depreciation_value = self.asset_id.value - self.asset_id.value_residual
