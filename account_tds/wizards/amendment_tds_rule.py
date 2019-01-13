# -*- coding: utf-8 -*-

from odoo import models, fields, api,_

class TDSRules(models.Model):
    _name = 'tds.rule.wizard'
    _order = 'name desc'
    _description = 'TDS Rule'

    @api.multi
    def _get_effective_from(self):
        return self._context['effective_from']

    @api.multi
    def _get_effective_end(self):
        return self._context['effective_end']

    @api.multi
    def _get_account_id(self):
        return self._context['account_id']

    @api.multi
    def _get_type_rate(self):
        return self._context['type_rate']

    @api.multi
    def _get_flat_rate(self):
        return self._context['flat_rate']

    @api.multi
    def _get_line_ids(self):
        return self._context['line_ids']

    @api.multi
    def _get_name(self):
        return self._context['name']

    name = fields.Char(string='Name',size=50,readonly=True, default = _get_name)
    active = fields.Boolean(string='Active',default = True)
    current_version = fields.Char('Current Version',readonly=True)
    account_id = fields.Many2one('account.account',string = "Tds Account",default=_get_account_id)
    #version_ids = fields.One2many('tds.rule.version', 'version_wizard_id',string="Versions Details")
    line_ids = fields.One2many('tds.rule.line','tds_rule_wiz_id',string='Rule Details',default=_get_line_ids)
    effective_from = fields.Date(string='Effective Date', required=True,default=_get_effective_from)
    effective_end = fields.Date(string='Effective End Date', required=True,default=_get_effective_end)
    type_rate = fields.Selection([
        ('flat', 'Flat Rate'),
        ('slab', 'Slab'),
    ], string='Tds Type', required=True,default=_get_type_rate)
    flat_rate = fields.Float(string='Rate',size=50,default=_get_flat_rate)


    @api.multi
    def generate_rule(self):
        rule_pool = self.env['tds.rule']
        rule_line_pool = self.env['tds.rule.line']
        version_pool = self.env['tds.rule.version']
        rule_list = rule_pool.browse([self._context['active_id']])
        for r in self:
            rule_obj = {
                'name': rule_list.env['ir.sequence'].get('name'),
                'effective_from': r.effective_from,
                'effective_end': r.effective_end,
                'type_rate': r.type_rate,
                'flat_rate': r.flat_rate,
                'rel_id': r.id,
            }
            rule_list.version_ids += self.env['tds.rule.version'].create(rule_obj)
        # for rule in self.line_ids:
        #     line_res = {
        #         'range_from': rule.range_from,
        #         'range_to': rule.range_to,
        #         'rate': rule.rate,
        #         'rel_id': rule.id
        #     }
        #     rule_list.version_ids.version_line_ids += self.env['tds.rule.version.line'].create(line_res)
