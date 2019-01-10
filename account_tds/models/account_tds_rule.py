# -*- coding: utf-8 -*-

from odoo import models, fields, api,_

class TDSRules(models.Model):
    _name = 'tds.rule'
    _order = 'name desc'
    _description = 'TDS Rule'

    name = fields.Char(string='Name',required=True,size=50)
    active = fields.Boolean(string='Active',default = True)
    current_version = fields.Char('Current Version',readonly=True)
    account_id = fields.Many2one('account.account',string = "Tds Account")
    version_ids = fields.One2many('tds.rule.version', 'tds_version_rule_id',string="Versions Details")
    line_ids = fields.One2many('tds.rule.line','tds_rule_id',string='Rule Details')
    effective_from = fields.Date(string='Effective Date', required=True)
    effective_end = fields.Date(string='Effective End Date', required=True)
    type_rate = fields.Selection([
        ('flat', 'Flat Rate'),
        ('slab', 'Slab'),
    ], string='Tds Type', required=True)
    flat_rate = fields.Float(string='Rate',size=50)

    state = fields.Selection([
        ('draft', "Draft"),
        ('confirm', "Confirm"),
    ], default='draft')

    @api.multi
    def action_confirm(self):
        self.state = 'confirm'


class TDSRuleVersion(models.Model):
    _name = 'tds.rule.version'
    _order = 'name desc'
    _description = 'TDS Rule Version'

    name = fields.Char(string='Name', required=True,size=50)
    active = fields.Boolean(string='Active',default=True)
    tds_version_rule_id = fields.Many2one('tds.rule')
    effective_from = fields.Date(string='Effective Date', required=True)
    effective_end = fields.Date(string='Effective End Date', required=True)
    type_rate = fields.Selection([
        ('flat', 'Flat Rate'),
        ('slab', 'Slab'),
    ], string='Tds Type',required=True)
    flat_rate = fields.Float(string='Rate',size=50)
    version_line_ids = fields.One2many('tds.rule.version.line','tds_version_id',string='Rule Details')



class TDSRuleLine(models.Model):
    _name = 'tds.rule.line'

    tds_rule_id = fields.Many2one('tds.rule')
    range_from = fields.Float(string='From Range',required=True)
    range_to = fields.Float(string='To Range',required=True)
    rate = fields.Float(string='Rate',required=True,size=50)

class TDSRuleVersionLine(models.Model):
    _name = 'tds.rule.version.line'

    tds_version_id = fields.Many2one('tds.rule.version')
    range_from = fields.Float(string='From Range',required=True)
    range_to = fields.Float(string='To Range',required=True)
    rate = fields.Float(string='Rate',required=True,size=50)



