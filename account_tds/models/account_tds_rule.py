# -*- coding: utf-8 -*-

from odoo import models, fields, api

class TDSRules(models.Model):
    _name = 'tds.rule'

    name = fields.Char(string='Name')
    active = fields.Boolean(string='Active')
    current_version = fields.Char('Current Version')
    version_ids = fields.One2many('tds.rule.version', 'tds_rule_id', string="Versions Details")


class TDSRuleVersion(models.Model):
    _name = 'tds.rule.version'

    name = fields.Char(string='Name')
    active = fields.Boolean(string='Active')
    tds_rule_id = fields.Many2one('tds.rule', ondelete='cascade')
    effective_date = fields.Date(string='Effective Date')
    type_rate = fields.Selection([
        ('flat', 'Flat Rate'),
        ('slab', 'Slab'),
    ], string='Type')
    rule_line_ids = fields.One2many('tds.rule.line','tds_version_id',string='Rule Details')


class TDSRuleLine(models.Model):
    _name = 'tds.rule.line'

    tds_version_id = fields.Many2one('tds.rule.version', ondelete='cascade')
    range_from = fields.Date(string='From Range')
    to_from = fields.Date(string='To Range')
    rate = fields.Float(string='Ra')



