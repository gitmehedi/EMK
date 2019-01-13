# -*- coding: utf-8 -*-

from odoo import models, fields, api,_

class TDSRules(models.Model):
    _name = 'tds.rule'
    _order = 'name desc'
    _description = 'TDS Rule'

    name = fields.Char(string='Name',required=True,size=50)
    active = fields.Boolean(string='Active',default = True)
    current_version = fields.Char('Current Version',readonly=True,compute = '_compute_version')
    account_id = fields.Many2one('account.account',string = "TDS Account")
    version_ids = fields.One2many('tds.rule.version', 'tds_version_rule_id',string="Versions Details")
    line_ids = fields.One2many('tds.rule.line','tds_rule_id',string='Rule Details')
    effective_from = fields.Date(string='Effective Date', required=True)
    effective_end = fields.Date(string='Effective End Date', required=True)
    type_rate = fields.Selection([
        ('flat', 'Flat Rate'),
        ('slab', 'Slab'),
    ], string='TDS Type', required=True)
    flat_rate = fields.Float(string='Rate',size=50)

    state = fields.Selection([
        ('draft', "Draft"),
        ('confirm', "Confirm"),
    ], default='draft')


    @api.multi
    def _compute_version(self):
        date = self._context.get('date') or fields.Date.today()
        for record in self:
            for rec in record.version_ids:
                if rec.effective_from <= date and rec.effective_end >= date:
                    record.current_version = rec.name
                else:
                    pass


    @api.multi
    def action_confirm(self):
        for rec in self:
            res = {
                'name': rec.env['ir.sequence'].get('name'),
                'active': rec.active,
                'effective_from': rec.effective_from,
                'effective_end': rec.effective_end,
                'type_rate': rec.type_rate,
                'flat_rate': rec.flat_rate,
                'rel_id': rec.id,
            }
            self.version_ids += self.env['tds.rule.version'].create(res)
        if self.type_rate == 'slab':
            for rule in self.line_ids:
                line_res = {
                    'range_from' : rule.range_from,
                    'range_to' : rule.range_to,
                    'rate' : rule.rate,
                    'rel_id': rule.id
                }
            self.version_ids.version_line_ids += self.env['tds.rule.version.line'].create(line_res)
        self.state = 'confirm'



class TDSRuleVersion(models.Model):
    _name = 'tds.rule.version'
    _order = 'name desc'
    _description = 'TDS Rule Version'

    emp_code_id = fields.Char(string='Code')
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



