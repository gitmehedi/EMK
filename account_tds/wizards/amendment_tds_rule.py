from odoo import models, fields, api,_

class TDSRules(models.Model):
    _name = 'tds.rule.wizard'
    _order = 'name desc'
    _description = 'TDS Rule'


    name = fields.Char(string='Name',size=50,readonly=True,default=lambda self: self.env.context.get('name'))
    active = fields.Boolean(string='Active',default=lambda self: self.env.context.get('active'))
    current_version = fields.Char('Current Version',readonly=True)
    account_id = fields.Many2one('account.account',string="Tds Account",default=lambda  self: self.env.context.get('account_id'))
    line_ids = fields.One2many('tds.rule.wizard.line','tds_rule_wiz_id',string='Rule Details',default=lambda self: self.env.context.get('line_ids'))
    effective_from = fields.Date(string='Effective Date', required=True,default=lambda self: self.env.context.get('effective_from'))
    effective_end = fields.Date(string='Effective End Date', required=True,default=lambda self: self.env.context.get('effective_end'))
    type_rate = fields.Selection([
        ('flat', 'Flat Rate'),
        ('slab', 'Slab'),
    ], string='Tds Type', required=True,default=lambda self: self.env.context.get('type_rate'))
    flat_rate = fields.Float(string='Rate',size=50,default=lambda  self: self.env.context.get('flat_rate'))


    @api.multi
    def generate_rule(self):
        rule_list = self.env['tds.rule'].browse([self._context['active_id']])
        rule_list.line_ids.unlink()
        rule_list.name = self.name
        rule_list.effective_from = self.effective_from
        rule_list.effective_end = self.effective_end
        rule_list.type_rate = self.type_rate
        rule_list.account_id = self.account_id.id
        if rule_list.flat_rate:
            rule_list.flat_rate = self.flat_rate

        #update Slab details
        slab_list = []
        for rec in self.line_ids:
            vals = {}
            vals['range_from'] = rec.range_from
            vals['range_to'] = rec.range_to
            vals['rate'] = rec.rate
            vals['tds_rule_wiz_id'] = rec.id
            slab_list.append(vals)
        rule_list.line_ids = slab_list

        # Create Version
        rule_obj = {
            'name': rule_list.env['ir.sequence'].get('name'),
            'effective_from': self.effective_from,
            'effective_end': self.effective_end,
            'type_rate': self.type_rate,
            'flat_rate': self.flat_rate,
            'rel_id': self.id,
        }
        rule_list.version_ids += self.env['tds.rule.version'].create(rule_obj)
        if self.type_rate == 'slab':
            for rule in self.line_ids:
                line_res = {
                    'range_from': rule.range_from,
                    'range_to': rule.range_to,
                    'rate': rule.rate,
                    'rel_id': rule.id
                }
            rule_list.version_ids[-1].version_line_ids += self.env['tds.rule.version.line'].create(line_res)

class TDSRuleWizardLine(models.Model):
    _name = 'tds.rule.wizard.line'

    tds_rule_wiz_id = fields.Many2one('tds.rule.wizard')
    range_from = fields.Float(string='From Range', required=True)
    range_to = fields.Float(string='To Range', required=True)
    rate = fields.Float(string='Rate', required=True, size=50)