# -*- coding: utf-8 -*-

from odoo import models, fields, api,_

class TDSRules(models.Model):
    _name = 'tds.rule'
    _order = 'name desc'
    _description = 'TDS Rule'

    name = fields.Char(string='Name',required=True,size=50)
    active = fields.Boolean(string='Active',default = False)
    current_version = fields.Char('Current Version',readonly=True)
    account_id = fields.Many2one('account.account',string = "Tds Account")
    version_ids = fields.One2many('tds.rule.version', 'tds_rule_id', string="Versions Details")
    line_ids = fields.One2many('tds.rule.line','tds_version_id',string='Rule Details')
    effective_from = fields.Date(string='Effective Date', required=True)
    effective_end = fields.Date(string='Effective End Date', required=True)
    type_rate = fields.Selection([
        ('flat', 'Flat Rate'),
        ('slab', 'Slab'),
    ], string='Tds Type', required=True)
    flat_rate = fields.Float(string='Rate')

    state = fields.Selection([
        ('draft', "Draft"),
        ('confirm', "Confirm"),
    ], default='draft')

    @api.multi
    def action_confirm(self):
        self.state = 'confirm'



                #
    # @api.multi
    # def _compute_version(self):
    #     date = self._context.get('date') or fields.Datetime.now()
    #     for rec in self.version_ids:
    #         if rec.effective_from <= date and rec.effective_end >= date:
    #             self.current_version = rec.name


class TDSRuleVersion(models.Model):
    _name = 'tds.rule.version'
    _order = 'name desc'
    _description = 'TDS Rule Version'

    name = fields.Char(string='Name', required=True,size=50)
    active = fields.Boolean(string='Active')
    tds_rule_id = fields.Many2one('tds.rule', ondelete='cascade')
    effective_from = fields.Date(string='Effective Date', required=True)
    effective_end = fields.Date(string='Effective End Date', required=True)
    type_rate = fields.Selection([
        ('flat', 'Flat Rate'),
        ('slab', 'Slab'),
    ], string='Tds Computation',required=True)
    flat_rate = fields.Float(string='Rate')
    rule_line_ids = fields.One2many('tds.rule.line','tds_version_id',string='Rule Details')



class TDSRuleLine(models.Model):
    _name = 'tds.rule.line'

    tds_version_id = fields.Many2one('tds.rule.version', ondelete='cascade')
    tds_rule_id = fields.Many2one('tds.rule', ondelete='cascade')
    range_from = fields.Float(string='From Range',required=True)
    range_to = fields.Float(string='To Range',required=True)
    rate = fields.Float(string='Rate',required=True)



