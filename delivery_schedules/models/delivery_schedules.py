import datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class DeliverySchedules(models.Model):
    _name = 'delivery.schedules'
    _description = 'Delivery Schedule'
    _inherit = ['mail.thread']
    _order = "id DESC"

    @api.depends('line_ids.scheduled_qty')
    def _amount_all(self):
        for ds in self:
            amount_total = 0.0
            for line in ds.line_ids:
                amount_total += line.scheduled_qty

            ds.scheduled_qty = amount_total

    name = fields.Char(string='Name',readonly=True,default='/')
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

    operating_unit_id = fields.Many2one('operating.unit',
                                        string='Operating Unit',
                                        required=True, readonly=True, states={'draft': [('readonly', False)]},
                                        track_visibility='onchange')

    line_ids = fields.One2many('delivery.schedules.line', 'parent_id', string="Delivery Schedule Line")

    scheduled_qty = fields.Float(string='Total Scheduled Qty.',
                                 compute='_amount_all',store=True,
                                 track_visibility='onchange')
    state = fields.Selection([
        ('draft', "Draft"),
        ('revision', "Revised"),
        ('approve', "Confirm"),
    ], default='draft', track_visibility='onchange')

    @api.onchange('operating_unit_id')
    def onchange_operating_unit_id(self):
        if self.state == 'draft':
            self.line_ids=[]

    @api.multi
    def action_approve(self):
        if not self.line_ids:
            raise ValidationError("Without Product Details information, you can't confirm it.")
        if self.name == '/':
            seq = self.env['ir.sequence'].next_by_code_new('delivery.schedule', self.requested_date, self.operating_unit_id)
            self.write({'name' : seq, 'origin' : seq,})
        res = {
            'state': 'approve',
            'approve_date': fields.Datetime.now(),
            'approved_by': self.env.user.id,
        }
        for line in self.line_ids:
            if line.state in ['draft','revision']:
                line.write({'state': 'approve','requested_date':self.requested_date})
        # email....................................................................
        email_server_obj = self.env['ir.mail_server'].search([], order='id ASC', limit=1)
        template = self.env.ref('delivery_schedules.schedule_email_template')
        template.write({
            'subject': "Delivery Instruction",
            'email_from': email_server_obj.name,
        })

        operation_groups_users = self.env['res.groups'].search([('name', '=', 'Delivery Operation')]).users
        operation_user_list = operation_groups_users.filtered(lambda x: x.default_operating_unit_id == self.operating_unit_id)
        if operation_user_list:
            for i in operation_user_list:
                if i.email:
                    template.write({
                        'email_to': i.email})
                    self.env['mail.template'].browse(template.id).send_mail(self.id)

        #      .............................................................................
        return self.write(res)

    @api.multi
    def action_draft(self):
        res = {
            'state': 'revision',
            'revision': self.revision + 01,
        }
        self.write(res)
        for line in self.line_ids:
            if line.state != 'done':
                line.write({'state': 'revision',})
        self.write({'name':self.origin+'/'+str(self.revision)})

    @api.multi
    def unlink(self):
        for entry in self:
            if entry.state != 'draft':
                raise UserError(_('After confirmation You can not delete this.'))
            elif entry.line_ids.filtered(lambda x: x.state == 'done'):
                raise UserError(_('You can not delete ,after Schedule line are done.'))
            entry.line_ids.unlink()
        return super(DeliverySchedules, self).unlink()

    @api.one
    @api.constrains('requested_date')
    def _check_requested_date(self):
        if self.requested_date < fields.Date.today():
            raise ValidationError(_("Requested date can't be back date entry"))
        elif self.requested_date > fields.Date.to_string(datetime.date.today() + relativedelta(days=7)):
            raise ValidationError(_("Requested date can't bigger then 7 days"))
        else:
            pass

    # ----------------------------------------------------------------------------------------------------------------------------
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


        ## Sales Person
        #####################################
        # @api.model
        # def _default_operating_unit(self):
        #     team = self.env['crm.team']._get_default_team_id()
        #     if team.operating_unit_id:
        #         return team.operating_unit_id
        # @api.model
        # def _default_sales_team(self):
        #     team = self.env['crm.team']._get_default_team_id()
        #     if team:
        #         return team.id
        #
        # sales_team_id = fields.Many2one('crm.team', string='Sales Team', readonly=True,
        #                                 default=_default_sales_team, track_visibility='onchange')

        ########################################
