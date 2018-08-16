from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError



class DeliverySchedules(models.Model):
    _name = 'delivery.schedules'
    _description = 'Delivery Schedule'
    _inherit = ['mail.thread']
    _order = "id DESC"

    name = fields.Char(string='Name', index=True, readonly=True)
    requested_date = fields.Date('Date', default=fields.Datetime.now,readonly=True,
                                 states={'draft': [('readonly', False)]},
                                 track_visibility='onchange')
    sequence_id = fields.Char('Sequence', readonly=True)
    requested_by = fields.Many2one('res.users', string='Requested By', readonly=True,
                                   default=lambda self: self.env.user)
    revision = fields.Integer(string='Revision',readonly = True,
                              help="Used to keep track of changes")
    origin = fields.Char('Origin', copy=False,help="Origin Name of the document.")
    approve_date = fields.Datetime('Approve Date', readonly=True,track_visibility='onchange')
    approved_by = fields.Many2one('res.users', string='Approver', readonly=True,
                                  help="who have approve.",track_visibility='onchange')

    ## Sales Person & OP Unit
    #####################################
    @api.model
    def _default_operating_unit(self):
        team = self.env['crm.team']._get_default_team_id()
        if team.operating_unit_id:
            return team.operating_unit_id

    operating_unit_id = fields.Many2one('operating.unit',
                                        string='Operating Unit',
                                        required=True, readonly=True,
                                        default=_default_operating_unit, track_visibility='onchange')

    @api.model
    def _default_sales_team(self):
        team = self.env['crm.team']._get_default_team_id()
        if team:
            return team.id

    sales_team_id = fields.Many2one('crm.team', string='Sales Team', readonly=True,
                                    default=_default_sales_team, track_visibility='onchange')

    ########################################


    line_ids = fields.One2many('delivery.schedules.line', 'parent_id', string="Products", readonly=True,
                               states={'draft': [('readonly', False)]},track_visibility='onchange')

    state = fields.Selection([
        ('draft', "Draft"),
        ('approve', "Confirm")
    ], default='draft', track_visibility='onchange')


    @api.model
    def create(self, vals):
        team = self.env['crm.team']._get_default_team_id()
        seq = self.env['ir.sequence'].next_by_code_new('delivery.schedule', self.requested_date,
                                                           team.operating_unit_id) or '/'
        vals['name'] = seq
        vals['origin'] = seq
        return super(DeliverySchedules, self).create(vals)


    @api.multi
    def action_approve(self):
        if not self.line_ids:
            raise ValidationError("Without Product Details information, you can't confirm it.")
        res = {
            'state': 'approve',
            'approve_date': fields.Datetime.now(),
            'approved_by': self.env.user.id,
        }
        for line in self.line_ids:
            if line.state in ['draft','revision']:
                line.write({'state': 'approve',})
        return self.write(res)

    @api.multi
    def action_draft(self):
        res = {
            'state': 'draft',
            'revision': self.revision + 01,
        }
        self.write(res)
        for line in self.line_ids:
            if line.state != 'done':
                line.write({'state': 'revision',})
        self.write({'name':self.origin+'-'+str(self.revision)})

    @api.multi
    def unlink(self):
        for entry in self:
            if entry.state != 'draft':
                raise UserError(_('After confirmation You can not delete this.'))
            elif entry.line_ids.filtered(lambda x: x.state == 'done'):
                raise UserError(_('You can not delete ,after Schedule line are done.'))
            entry.line_ids.unlink()
        return super(DeliverySchedules, self).unlink()


    @api.constrains('name')
    def _check_unique_constraint(self):
        if self.name:
            filters = [['name', '=ilike', self.name]]
            name = self.search(filters)
            if len(name) > 1:
                raise Warning('[Unique Error] Name must be unique!')

    @api.multi
    def generate_schedule_letter(self):

        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('delivery_schedules', 'schedule_email_template')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict()
        ctx.update({
            'default_model': 'delivery.schedules',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'custom_layout': "delivery_schedules.schedule_email_template"
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }
