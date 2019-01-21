from odoo import models, fields, api,_
from datetime import datetime

from odoo.exceptions import UserError, ValidationError


class TDSRules(models.Model):
    _name = 'tds.rule'
    _inherit = ['mail.thread']
    _order = 'name desc'
    _description = 'TDS Rule'

    name = fields.Char(string='Name',required=True,size=50,
                       track_visibility='onchange', states={'confirm':[('readonly', True)]})
    active = fields.Boolean(string='Active',default = True,
                            track_visibility='onchange',states={'confirm':[('readonly', True)]})
    current_version = fields.Char('Current Version',readonly=True,compute='_compute_current_version',
                                  states={'confirm':[('readonly', True)]})
    account_id = fields.Many2one('account.account',string = "TDS Account",required=True,
                                 track_visibility='onchange',states={'confirm':[('readonly', True)]})
    version_ids = fields.One2many('tds.rule.version', 'tds_version_rule_id',string="Versions Details",states={'confirm':[('readonly', True)]})
    line_ids = fields.One2many('tds.rule.line','tds_rule_id',string='Rule Details',states={'confirm':[('readonly', True)]})
    effective_from = fields.Date(string='Effective Date', required=True,
                                 track_visibility='onchange',states={'confirm':[('readonly', True)]})
    # effective_end = fields.Date(string='Effective To Date', required=False,
    #                             track_visibility='onchange',states={'confirm':[('readonly', True)]})
    type_rate = fields.Selection([
        ('flat', 'Flat Rate'),
        ('slab', 'Slab'),
    ], string='TDS Type', required=True,track_visibility='onchange',states={'confirm':[('readonly', True)]})
    flat_rate = fields.Float(string='Rate',size=50,
                             track_visibility='onchange',states={'confirm':[('readonly', True)]})

    state = fields.Selection([
        ('draft', "Draft"),
        ('confirm', "Confirm"),
    ], default='draft')

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'This Name is already in use'),
    ]

    @api.multi
    def _compute_current_version(self):
        date = self._context.get('date') or fields.Date.today()
        for record in self:
            for rec in record.version_ids:
                if rec.effective_from == date:
                    record.current_version = rec.name
                else:
                    pass

    @api.model
    def compute_version(self):
        vals = []
        today = datetime.now()
        rule = self.env['tds.rule'].search([])
        for record in rule:
            for rec in record.version_ids:
                date = datetime.strptime(rec.effective_from, "%Y-%m-%d")
                if today.day == date.day and today.month == date.month and today.year == date.year:
                    if rec.active == True:
                        record.effective_from = rec.effective_from
                        record.type_rate = rec.type_rate
                        record.account_id = rec.account_id.id
                        if record.flat_rate:
                            record.flat_rate = rec.flat_rate
                        if rec.version_line_ids:
                            for obj in rec.version_line_ids:
                                vals.append((0, 0, {'range_from': obj.range_from,
                                                    'range_to': obj.range_to,
                                                    'rate': obj.rate,
                                                    }))

                            record.line_ids.unlink()
                            record.line_ids = vals
        return




    @api.constrains('flat_rate','line_ids')
    def _check_flat_rate(self):
        for rec in self:
            if rec.state == 'draft':
                if rec.type_rate == 'flat':
                    if rec.flat_rate < 0:
                        raise ValidationError("Please Check Your Tds Rate!! \n Rate Never Take Negative Value!")
                elif rec.type_rate == 'slab':
                    if len(rec.line_ids) <= 0:
                        raise ValidationError("Please, Add Slab Details ")
                    elif len(rec.line_ids) > 0:
                        for line in rec.line_ids:
                            if line.range_from >= line.range_to:
                                raise ValidationError("Please Check Your Slab Range!! \n 'Range From' Never Be Greater Than or Equal 'Range To'")
                            elif line.rate <0:
                                raise ValidationError("Please Check Your Slab's Tds Rate!! \n Rate Never Take Negative Value!")
                            elif line.range_from <0:
                                raise ValidationError("Please Check Your Slab's Tds Rate!! \n Rate Never Take Negative Value!")
                            elif line.range_to <0:
                                raise ValidationError("Please Check Your Slab's Tds Rate!! \n Rate Never Take Negative Value!")


    @api.onchange('type_rate')
    def _check_type_rate(self):
        self.flat_rate = 0
        self.line_ids = []


    @api.multi
    def action_confirm(self):
        for rec in self:
            num = 1
            seq = self.name + ' / 000' + str(num)
            res = {
                'name': seq,
                'active': rec.active,
                'effective_from': rec.effective_from,
                'account_id': self.account_id.id,
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
            slab_list.append(vals)
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
    account_id = fields.Many2one('account.account',string="Tds Account",required=True)
    effective_from = fields.Date(string='Effective Date', required=True)
    #effective_end = fields.Date(string='Effective End Date', required=False)
    type_rate = fields.Selection([
        ('flat', 'Flat Rate'),
        ('slab', 'Slab'),
    ], string='Tds Type',required=True)
    flat_rate = fields.Float(string='Rate',size=50)
    version_line_ids = fields.One2many('tds.rule.version.line','tds_version_id',string='Rule Details')



class TDSRuleLine(models.Model):
    _name = 'tds.rule.line'

    tds_rule_id = fields.Many2one('tds.rule')
    range_from = fields.Integer(string='From Range',required=True)
    range_to = fields.Integer(string='To Range',required=True)
    rate = fields.Float(string='Rate',required=True,size=50)

    @api.constrains('range_from', 'range_to')
    def _check_time(self):
        for rec in self:
            domain = [
                ('range_from', '<', rec.range_to),
                ('range_to', '>', rec.range_from),
                ('id', '!=', rec.id),
                ('tds_rule_id', '=', rec.tds_rule_id.id)
            ]
            check_domain = self.search_count(domain)
            if check_domain:
                date_time_range_from = str(rec.range_from)
                date_time_range_to = str(rec.range_to)
                raise ValidationError(_(
                    " The Range (%s)  and  (%s)  are overlapping with existing Slab ." % (
                        date_time_range_from, date_time_range_to)
                ))


class TDSRuleVersionLine(models.Model):
    _name = 'tds.rule.version.line'

    tds_version_id = fields.Many2one('tds.rule.version')
    range_from = fields.Integer(string='From Range',required=True)
    range_to = fields.Integer(string='To Range',required=True)
    rate = fields.Float(string='Rate',required=True,size=50)



