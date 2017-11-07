from odoo import api, fields, models, _

class LcRevision(models.Model):
    _inherit = "letter.credit"
   
    current_revision_id = fields.Many2one('letter.credit','Current revision',readonly=True,copy=True, ondelete='cascade')
    old_revision_ids = fields.One2many('letter.credit','current_revision_id','Old revisions',readonly=True,context={'active_test': False})
    revision_number = fields.Integer('Revision', copy=False)
    unrevisioned_name = fields.Char('LC Reference',copy=True,readonly=True)
    active = fields.Boolean('Active',default=True,copy=True)    
    
    @api.model
    def create(self, vals):
        if 'unrevisioned_name' not in vals:
            if vals.get('name', 'New') == 'New':
                seq = self.env['ir.sequence']
                vals['name'] = seq.next_by_code('letter.credit') or '/'
            vals['unrevisioned_name'] = vals['name']
        return super(LcRevision, self).create(vals)
    
    @api.multi
    def action_revision(self):
        self.ensure_one()
        view_ref = self.env['ir.model.data'].get_object_reference('gbs_lc', 'view_local_credit_form')
        view_id = view_ref and view_ref[1] or False,
        self.with_context(new_lc_revision=True).copy()
        self.write({'state': self.state,'status':'amendment'})
        return {
            'type': 'ir.actions.act_window',
            'name': _('LC'),
            'res_model': 'letter.credit',
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
        if not defaults:
            defaults = {}
        if self.env.context.get('new_lc_revision'):
            prev_name = self.name
            revno = self.revision_number
            self.write({'revision_number': revno + 1,'name': '%s-%02d' % (self.unrevisioned_name,revno + 1)})
            defaults.update({'name': prev_name,'revision_number': revno,'active': False,'state': 'amendment','current_revision_id': self.id,'unrevisioned_name': self.unrevisioned_name,})
        return super(LcRevision, self).copy(defaults)




    
   
