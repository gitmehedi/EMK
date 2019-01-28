# -*- coding: utf-8 -*-

import calendar
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.tools import float_compare, float_is_zero


class AccountAssetDisposal(models.Model):
    _name = 'account.asset.disposal'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _rec = 'id desc'
    _rec_name = 'name'

    name = fields.Char(string='Disponal Sequence')
    total_value = fields.Float(string='Total Asset Value', required=True, digits=(14, 2))
    total_depreciation_amount = fields.Float(string='Total Depreciation Value', required=True, digits=(14, 2))
    request_date = fields.Datetime(string='Request Date', required=True, default=fields.Datetime.now())
    approve_date = fields.Datetime(string='Approve Date')
    dispose_date = fields.Datetime(string='Dispose Date')
    request_user_id = fields.Many2one('res.users', string='Request User', required=True,
                                      default=lambda self: self.env.user)
    approve_user_id = fields.Many2one('res.users', string='Approve User')
    dispose_user_id = fields.Many2one('res.users', string='Dispose User')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id.id)

    line_ids = fields.One2many('account.asset.disposal.line', 'dispose_id', string='Disposal Line')
    state = fields.Selection([('draft', 'Draft'), ('approve', 'Approved'), ('done', 'Done')], default='draft',
                             string='State')


class AccountAssetDisposalLine(models.Model):
    _name = 'account.asset.disposal.line'
    _rec = 'id ASC'

    asset_id = fields.Many2one('account.asset.asset', string='Asset Name')
    asset_value = fields.Float(string='Asset Value', required=True, digits=(14, 2))
    depreciation_value = fields.Float(string='Depreciation Value', required=True, digits=(14, 2))

    dispose_id = fields.Many2one('account.asset.disposal', string='Disposal', ondelete='restrict')
    journal_entry = fields.Selection([('unpost', 'Unposted'), ('post', 'Posted')], default='unpost', requried=True)