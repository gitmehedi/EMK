# -*- coding: utf-8 -*-

from odoo import models, fields, api,_

class TDSRules(models.Model):
    _name = 'tds.rule'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'name desc'
    _description = 'TDS Rule'

    name = fields.Char(string='Name',required=True,size=50, states={'confirm':[('readonly', True)]})
    active = fields.Boolean(string='Active',default = True,states={'confirm':[('readonly', True)]})
    current_version = fields.Char('Current Version',readonly=True,compute = '_compute_version',states={'confirm':[('readonly', True)]})
    account_id = fields.Many2one('account.account',string = "TDS Account",states={'confirm':[('readonly', True)]})
    version_ids = fields.One2many('tds.rule.version', 'tds_version_rule_id',string="Versions Details",states={'confirm':[('readonly', True)]})
    line_ids = fields.One2many('tds.rule.line','tds_rule_id',string='Rule Details',states={'confirm':[('readonly', True)]})
    effective_from = fields.Date(string='Effective Date', required=True,states={'confirm':[('readonly', True)]})
    effective_end = fields.Date(string='Effective End Date', required=True,states={'confirm':[('readonly', True)]})
    type_rate = fields.Selection([
        ('flat', 'Flat Rate'),
        ('slab', 'Slab'),
    ], string='TDS Type', required=True,states={'confirm':[('readonly', True)]})
    flat_rate = fields.Float(string='Rate',size=50,states={'confirm':[('readonly', True)]})

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

    @api.multi
    def action_amendment(self):
        slab_list = []
        for rec in self.line_ids:
            vals = {}
            vals['range_from'] = rec.range_from
            vals['range_to'] = rec.range_to
            vals['rate'] = rec.rate
            vals['tds_rule_wiz_id'] = rec.id
            slab_list.append(vals)
        self.line_ids = slab_list
        res = self.env.ref('account_tds.view_tds_rule_form_wizard')
        result = {
            'name': _('TDS Rule'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'tds.rule.wizard',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'context': {'name': self.name or False,
                        'effective_from': self.effective_from or False,
                        'effective_end': self.effective_end or False,
                        'type_rate': self.type_rate or False,
                        'active': self.active or False,
                        'account_id': self.account_id.id or False,
                        'line_ids': slab_list,
                        'flat_rate': self.flat_rate or False,
                        },
        }
        return result



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



