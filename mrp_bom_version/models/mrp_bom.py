# imports of odoo
from odoo import models, fields, api, _


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    name = fields.Char(string='BOM Number', readonly=True, default='/')
    active = fields.Boolean(string='Active', default=True, copy=True, readonly=True)
    historical_date = fields.Date(string='Historical Date', readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('historical', 'Historical')
    ], string='State', readonly=True, default='draft')

    version = fields.Integer(readonly=True, copy=False, default=0)
    base_name = fields.Char(string='BOM Reference', readonly=True)
    parent_bom_id = fields.Many2one('mrp.bom', string='Parent BOM', copy=True, ondelete='cascade')
    old_version_ids = fields.One2many('mrp.bom', 'parent_bom_id', string='Old Versions', readonly=True, context={'active_test': False})

    @api.multi
    def action_confirm(self):
        self.write({
            'state': 'confirmed'
        })

    @api.multi
    def action_new_version(self):
        res = self.env.ref('mrp_bom_version.view_mrp_bom_wizard_form')
        result = {
            'name': _('Please Enter The Information'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'mrp.bom.wizard',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
        }
        return result

    @api.multi
    def action_create_new_version(self, historical_date=None):
        self.ensure_one()
        view_ref = self.env['ir.model.data'].get_object_reference('mrp_bom_version', 'mrp_bom_version_form_view')
        view_id = view_ref and view_ref[1] or False,
        self.with_context(new_bom_version=True, historical_date=historical_date).copy()
        self.write({'state': self.state})

        return {
            'type': 'ir.actions.act_window',
            'name': _('BOM'),
            'res_model': 'mrp.bom',
            'res_id': self.id,
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'current',
            'nodestroy': True,
            'flags': {'initial_mode': 'edit'},
        }

    @api.returns('self', lambda value: value.id)
    @api.multi
    def copy(self, defaults=None):
        if self.env.context.get('new_bom_version'):
            defaults = {}
            previous_name = self.name
            version = self.version
            self.write({'version': version + 1, 'name': '%s-%02d' % (self.base_name, version + 1)})
            defaults.update({
                'parent_bom_id': self.id,
                'name': previous_name,
                'version': version,
                'active': False,
                'state': 'historical',
                'historical_date': self.env.context.get('historical_date') or fields.Date.today()
            })

        return super(MrpBom, self).copy(defaults)

    @api.model
    def create(self, vals):
        if 'name' not in vals:
            vals['name'] = self.env['ir.sequence'].next_by_code('mrp.bom') or _('New')

        if 'base_name' not in vals:
            vals['base_name'] = vals['name']

        return super(MrpBom, self).create(vals)
