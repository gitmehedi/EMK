from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class TDSRulesWizard(models.TransientModel):
    _name = 'tds.rule.wizard'
    _order = 'name desc'
    _description = 'TDS Rule'

    name = fields.Char(string='Name', size=200, readonly=True, default=lambda self: self.env.context.get('name'))
    active = fields.Boolean(string='Active', default=lambda self: self.env.context.get('active'))
    current_version = fields.Char('Current Version', readonly=True)
    account_id = fields.Many2one('account.account', string="TDS Account", required=True,
                                 default=lambda self: self.env.context.get('account_id'))
    line_ids = fields.One2many('tds.rule.wizard.line', 'tds_rule_wiz_id', string='Rule Details',
                               default=lambda self: self.env.context.get('line_ids'))
    effective_from = fields.Date(string='Effective Date', required=True,
                                 default=lambda self: self.env.context.get('effective_from'))
    type_rate = fields.Selection([
        ('flat', 'Flat Rate'),
        ('slab', 'Slab'),
    ], string='TDS Type', required=True, default=lambda self: self.env.context.get('type_rate'))
    flat_rate = fields.Float(string='Rate', size=3, default=lambda self: self.env.context.get('flat_rate'))
    price_include = fields.Boolean(string='Included in Price',
                                   default=lambda self: self.env.context.get('price_include'),
                                   help="Check this if the price you use on the product and invoice includes this TAX.")
    price_exclude = fields.Boolean(string='Excluded in Price',
                                   default=lambda self: self.env.context.get('price_exclude'),
                                   help="Check this if the price you use on the product and invoice exclude this TAX.")

    @api.multi
    def generate_rule(self):
        rule_list = self.env['tds.rule'].browse([self._context['active_id']])

        # Create Version
        length = len(rule_list.version_ids) + 1
        seq = rule_list.name + ' / 000' + str(length)
        rule_obj = {
            'name': seq,
            'effective_from': self.effective_from,
            'account_id': self.account_id.id,
            'type_rate': self.type_rate,
            'flat_rate': self.flat_rate,
            'price_include': self.price_include,
            'price_exclude': self.price_exclude,
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
        return rule_list.write({'is_amendment':True,'maker_id': self.env.user.id})

    @api.constrains('effective_from')
    def _check_effective_from(self):
        date = fields.Date.today()
        if self.effective_from:
            if self.effective_from < date:
                raise ValidationError(
                    "Please Check Effective Date!! \n 'Effective Date' must be greater than current date")

    @api.constrains('flat_rate', 'line_ids')
    def _check_flat_rate(self):
        for rec in self:
            if rec.type_rate == 'flat':
                if rec.flat_rate < 0:
                    raise ValidationError("Please Check Your Tds Rate!! \n Rate never take negative value!")
                elif rec.flat_rate > 100:
                    raise ValidationError("Please Check Your Tds Rate!! \n Rate never take more than 100%!")

            elif rec.type_rate == 'slab':
                if len(rec.line_ids) <= 0:
                    raise ValidationError(
                        "Please, Add Slab Details!! \n Make sure slab values('Range from','Range to') must be number.")
                elif len(rec.line_ids) > 0:
                    for line in rec.line_ids:
                        if line.range_from >= line.range_to:
                            raise ValidationError(
                                "Please Check Your Slab Range!! \n 'Range From' Never Be Greater Than or Equal 'Range To'")
                        elif line.rate < 0:
                            raise ValidationError(
                                "Please Check Your Slab's Tds Rate!! \n Rate never take  negative value!")
                        elif line.range_from < 0:
                            raise ValidationError(
                                "Please Check Your Slab's Tds Rate!! \n Rate Never Take Negative Value!")
                        elif line.range_to < 0:
                            raise ValidationError(
                                "Please Check Your Slab's Tds Rate!! \n Rate Never Take Negative Value!")


class TDSRuleWizardLine(models.TransientModel):
    _name = 'tds.rule.wizard.line'

    tds_rule_wiz_id = fields.Many2one('tds.rule.wizard')
    range_from = fields.Integer(string='From Range')
    range_to = fields.Integer(string='To Range')
    rate = fields.Float(string='Rate', digits=(12, 2))

    @api.constrains('range_from', 'range_to')
    def _check_time(self):
        for rec in self:
            domain = [
                ('range_from', '<', rec.range_to),
                ('range_to', '>', rec.range_from),
                ('id', '!=', rec.id),
                ('tds_rule_wiz_id', '=', rec.tds_rule_wiz_id.id)
            ]
            check_domain = self.search_count(domain)
            if check_domain:
                date_time_range_from = str(rec.range_from)
                date_time_range_to = str(rec.range_to)
                raise ValidationError(_(
                    " The Range (%s)  and  (%s)  are overlapping with existing Slab ." % (
                        date_time_range_from, date_time_range_to)
                ))