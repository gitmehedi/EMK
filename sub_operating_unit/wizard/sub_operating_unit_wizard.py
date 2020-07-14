from odoo import models, fields, api, _
from odoo.exceptions import Warning


class SubOperatingUnitWizard(models.TransientModel):
    _name = 'sub.operating.unit.wizard'

    @api.model
    def default_name(self):
        context = self._context
        return self.env[context['active_model']].search([('id', '=', context['active_id'])]).name

    @api.model
    def default_status(self):
        context = self._context
        return self.env[context['active_model']].search([('id', '=', context['active_id'])]).active

    status = fields.Boolean(string='Active', default=default_status)
    name = fields.Char(string='Requested Name')
    excl_branch_ids = fields.Many2many('operating.unit', 'wiz_seq_branch_excl_rel', string='Exclude Branch')
    inc_branch_ids = fields.Many2many('operating.unit', 'wiz_seq_branch_inc_rel', string='Include Branch')
    all_branch = fields.Boolean(string='All Branch', default=True)

    @api.constrains('name')
    def _check_unique_constrain(self):
        if self.name:
            code = self.env[self._context['active_model']].search([('id', '=', self._context['active_id'])]).code
            name = self.env['sub.operating.unit'].search(
                [('name', '=ilike', self.name.strip()), ('code', '=ilike', code),
                 ('state', '!=', 'reject'), '|', ('active', '=', True),
                 ('active', '=', False)])
            if len(name) == 1:
                raise Warning(_(
                    '[Unique Error] Combination of Name [{0}] and Code [{0q}] must be unique!'.format(self.name, code)))

    @api.onchange("name", "code")
    def onchange_strips(self):
        if self.name:
            self.name = str(self.name.strip()).upper()

    @api.multi
    def act_change_req(self):
        id = self._context['active_id']

        pending = self.env['history.sub.operating.unit'].search([('state', '=', 'pending'), ('line_id', '=', id)])
        if len(pending) > 0:
            raise Warning('[Warning] You already have a pending request!')

        self.env['history.sub.operating.unit'].create(
            {'change_name': self.name,
             'status': self.status,
             'excl_branch_ids': [(4, val.id) for val in self.excl_branch_ids],
             'inc_branch_ids': [(4, rec.id) for rec in self.inc_branch_ids],
             'all_branch': self.all_branch,
             'request_date': fields.Datetime.now(),
             'line_id': id})
        record = self.env['sub.operating.unit'].search(
            [('id', '=', id), '|', ('active', '=', False), ('active', '=', True)])
        if record:
            record.write({'pending': True, 'maker_id': self.env.user.id})
