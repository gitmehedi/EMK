from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError


class TDSRules(models.Model):
    _name = 'tds.rule'
    _inherit = ['mail.thread']
    _order = 'id desc'
    _description = 'TDS Rule'

    name = fields.Char(string='Name', required=True, size=200,
                       track_visibility='onchange', states={'confirm': [('readonly', True)]})
    active = fields.Boolean(string='Active', default=True,
                            track_visibility='onchange', states={'confirm': [('readonly', True)]})
    current_version = fields.Char('Current Version', readonly=True, compute='_compute_current_version')
    account_id = fields.Many2one('account.account', string="TDS Account", required=True,
                                 track_visibility='onchange', states={'confirm': [('readonly', True)]})
    version_ids = fields.One2many('tds.rule.version', 'tds_version_rule_id', string="Versions Details",
                                  states={'confirm': [('readonly', True)]})
    line_ids = fields.One2many('tds.rule.line', 'tds_rule_id', string='Rule Details',
                               states={'confirm': [('readonly', True)]})
    effective_from = fields.Date(string='Effective Date', required=True,default=fields.Datetime.now,
                                 track_visibility='onchange', states={'confirm': [('readonly', True)]})
    type_rate = fields.Selection([
        ('flat', 'Flat Rate'),
        ('slab', 'Slab'),
    ], string='TDS Type', required=True, track_visibility='onchange', states={'confirm': [('readonly', True)]})
    flat_rate = fields.Float(string='Rate', size=3,
                             track_visibility='onchange', states={'confirm': [('readonly', True)]})
    price_include = fields.Boolean(string='Included in Price', default=False,
                                   track_visibility='onchange', states={'confirm': [('readonly', True)]},
                                   help="Check this if the price you use on the product and invoices includes this TAX.")
    price_exclude = fields.Boolean(string='Excluded in Price', default=False,
                                   track_visibility='onchange', states={'confirm': [('readonly', True)]},
                                   help="Check this if the price you use on the product and invoices excludes this TAX.")
    effect_on_base = fields.Boolean(string='Effect On Base Price', default=False,
                                    track_visibility='onchange', states={'confirm': [('readonly', True)]},
                                    help="Check this if the TDS effect on base price.")
    state = fields.Selection([
        ('draft', "Draft"),
        ('confirm', "Confirmed"),
    ], default='draft',string="Status",track_visibility='onchange')
    is_amendment = fields.Boolean(default=False, string="Is Amendment",
                                  help="Take decision that, this agreement is amendment.")
    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit',
                                        states = {'confirm': [('readonly', True)]})
    maker_id = fields.Many2one('res.users', 'Maker', default=lambda self: self.env.user.id, track_visibility='onchange')
    approver_id = fields.Many2one('res.users', 'Checker', track_visibility='onchange')
    company_id = fields.Many2one('res.company', string='Company', readonly=True,
                                 default=lambda self: self.env.user.company_id)

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'This Name is already in use'),
    ]

    @api.constrains('name')
    def _check_unique_constrain(self):
        if self.name:
            name = self.search(
                [('name', '=ilike', self.name.strip()), ('state', '!=', 'reject'), '|', ('active', '=', True), ('active', '=', False)])
            if len(name) > 1:
                raise Warning('[Unique Error] Name must be unique!')

    @api.onchange("name")
    def onchange_strips(self):
        if self.name:
            self.name = self.name.strip()

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_('You cannot delete a record which is not in draft state!'))
        return super(TDSRules, self).unlink()

    @api.multi
    @api.depends('version_ids.state')
    def _compute_current_version(self):
        for record in self:
            if record.version_ids:
                record.current_version = self.version_ids.search([('state', '=', 'confirm'),
                                                                  ('tds_version_rule_id', '=', record.id)],order='id desc', limit=1).name


    @api.constrains('flat_rate', 'line_ids')
    def _check_flat_rate(self):
        for rec in self:
            if rec.state == 'draft':
                if rec.type_rate == 'flat':
                    if rec.flat_rate < 0:
                        raise ValidationError("Please Check Your TDS Rate!! \n Rate Never Take Negative Value!")
                    elif rec.flat_rate > 100:
                        raise ValidationError("Please Check Your TDS Rate!! \n Rate never take more than 100%!")
                elif rec.type_rate == 'slab':
                    if not rec.line_ids:
                        raise ValidationError(
                            "Please, Add Slab Details!! \n Make sure slab('Range from','Range to')values must be number.")
                    elif len(rec.line_ids) > 0:
                        for line in rec.line_ids:
                            if line.range_from >= line.range_to:
                                raise ValidationError(
                                    "Please Check Your Slab Range!! \n 'Range From' Never Be Greater Than or Equal 'Range To'")
                            elif line.rate < 0:
                                raise ValidationError(
                                    "Please Check Your Slab's TDS Rate!! \n Rate Never Take Negative Value!")
                            elif line.range_from < 0:
                                raise ValidationError(
                                    "Please Check Your Slab's TDS Rate!! \n Rate Never Take Negative Value!")
                            elif line.range_to < 0:
                                raise ValidationError(
                                    "Please Check Your Slab's TDS Rate!! \n Rate Never Take Negative Value!")

    @api.onchange('type_rate')
    def _check_type_rate(self):
        self.flat_rate = 0
        self.line_ids = []

    @api.multi
    def action_confirm(self):
        for rec in self:
            if rec.env.user.id == rec.maker_id.id and rec.env.user.id != SUPERUSER_ID:
                raise ValidationError(_("[Validation Error] Maker and Approver can't be same person!"))
            num = 1
            seq = rec.name + ' / 000' + str(num)
            res = {
                'name': seq,
                'active': rec.active,
                'effective_from': rec.effective_from,
                'account_id': rec.account_id.id,
                'type_rate': rec.type_rate,
                'flat_rate': rec.flat_rate,
                'rel_id': rec.id,
                'state': 'confirm',
                'approver_id': rec.env.user.id,
            }
            rec.version_ids += self.env['tds.rule.version'].create(res)
            if rec.type_rate == 'slab':
                for rule in rec.line_ids:
                    line_res = {
                        'range_from': rule.range_from,
                        'range_to': rule.range_to,
                        'rate': rule.rate,
                        'rel_id': rule.id
                    }
                    rec.version_ids[-1].version_line_ids += self.env['tds.rule.version.line'].create(line_res)
            rec.state = 'confirm'

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
                        'price_include': self.price_include or False,
                        'price_exclude': self.price_exclude or False,
                        },
        }
        return result

    @api.multi
    def action_approve_amendment(self):
        if self.env.user.id == self.maker_id.id and self.env.user.id != SUPERUSER_ID:
            raise ValidationError(_("[Validation Error] Editor and Approver can't be same person!"))
        if self.is_amendment == True:
            requested = self.version_ids.search([('state', '=', 'pending'),
                                                 ('tds_version_rule_id', '=', self.id)],
                                                order='id desc', limit=1)
            if requested:
                self.write({
                    'effective_from': requested.effective_from,
                    'type_rate': requested.type_rate,
                    'account_id': requested.account_id.id,
                    'approver_id': self.env.user.id,
                })
                if requested.type_rate == 'flat' and requested.flat_rate:
                    self.flat_rate = requested.flat_rate
                    self.price_include = requested.price_include
                    self.price_exclude = requested.price_exclude
                elif requested.type_rate == 'slab' and requested.version_line_ids:
                    vals = []
                    for ver_line in requested.version_line_ids:
                        vals.append((0, 0, {'range_from': ver_line.range_from,
                                            'range_to': ver_line.range_to,
                                            'rate': ver_line.rate,
                                            }))
                    self.line_ids.unlink()
                    self.line_ids = vals
                self.write({'is_amendment': False})
                requested.write({'state': 'confirm'})

    @api.constrains('effective_from')
    def _check_effective_from(self):
        date = fields.Date.today()
        if self.effective_from and not self.is_amendment:
            if self.effective_from < date:
                raise ValidationError(
                    "Please Check Effective Date!! \n 'Effective Date' must be greater than current date")

    @api.constrains('name')
    def _check_unique_constrain(self):
        if self.name:
            name = self.search(
                [('name', '=ilike', self.name.strip()), ('state', '!=', 'reject'), '|', ('active', '=', True), ('active', '=', False)])
            if len(name) > 1:
                raise Warning('[Unique Error] Name must be unique!')

    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {}, name=_('%s (copy)') % self.name)
        return super(TDSRules, self).copy(default)


class TDSRuleVersion(models.Model):
    _name = 'tds.rule.version'
    _order = 'name desc'
    _description = 'TDS Rule Version'

    emp_code_id = fields.Char(string='Code')
    name = fields.Char(string='Name', required=True, size=200)
    active = fields.Boolean(string='Active', default=True)
    tds_version_rule_id = fields.Many2one('tds.rule')
    account_id = fields.Many2one('account.account', string="TDS Account", required=True)
    effective_from = fields.Date(string='Effective Date', required=True)
    type_rate = fields.Selection([
        ('flat', 'Flat Rate'),
        ('slab', 'Slab'),
    ], string='TDS Type', required=True)
    flat_rate = fields.Float(string='Rate', digits=(13,2))
    version_line_ids = fields.One2many('tds.rule.version.line', 'tds_version_id', string='Rule Details')
    state = fields.Selection([
        ('pending', "Pending"),
        ('confirm', "Confirmed")], default='pending', string="Status")
    price_include = fields.Boolean(string='Included in Price', default=False)
    price_exclude = fields.Boolean(string='Excluded in Price', default=False)


class TDSRuleLine(models.Model):
    _name = 'tds.rule.line'

    tds_rule_id = fields.Many2one('tds.rule')
    range_from = fields.Integer(string='From Range', required=True)
    range_to = fields.Integer(string='To Range', required=True)
    rate = fields.Float(string='Rate', required=True, digits=(13,2))

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
    range_from = fields.Integer(string='From Range', required=True)
    range_to = fields.Integer(string='To Range', required=True)
    rate = fields.Float(string='Rate', required=True, digits=(12,2))

    # automated version for previous
    # @api.model
    # def compute_version(self):
    #     today = fields.Date.today()
    #     rule = self.env['tds.rule'].search([])
    #     for record in rule:
    #         for ver in record.version_ids:
    #             if today == ver.effective_from:
    #                 record.effective_from = ver.effective_from
    #                 record.type_rate = ver.type_rate
    #                 record.account_id = ver.account_id.id
    #                 if ver.type_rate == 'flat':
    #                     if ver.flat_rate:
    #                         record.flat_rate = ver.flat_rate
    #                 else:
    #                     if ver.version_line_ids:
    #                         vals = []
    #                         for ver_line in ver.version_line_ids:
    #                             vals.append((0, 0, {'range_from': ver_line.range_from,
    #                                                 'range_to': ver_line.range_to,
    #                                                 'rate': ver_line.rate,
    #                                                 }))
    #                         record.line_ids.unlink()
    #                         record.line_ids = vals
    #     return


    # @api.multi
    # def _compute_current_version(self):
    #     date = self._context.get('date') or fields.Date.today()
    #     for record in self:
    #         for rec in record.version_ids:
    #             if rec.effective_from == date:
    #                 record.current_version = rec.name
    #             else:
    #                 pass