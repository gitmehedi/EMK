from odoo import models, fields, api, exceptions,_


class ConfigureEmpChecklist(models.Model):
    _name = "hr.checklist.generate.popup"

    checklist_item_ids= fields.Many2many('hr.exit.checklist.item')

    @api.multi
    def compute_sheet(self, vals):

        active_id = vals['active_id']
        status_poll = self.env['hr.checklist.status']

        # if not self.checklist_item_ids:
        #     raise osv.except_osv(_("Warning!"), _("You must select items to generate checklist"))
        for item in self.browse(self['checklist_item_ids']):
            res = {
                'checklist_status_item_id': item.id.id,
                'checklist_type_id':item.id.checklist_type.id,
                'item_description':item.id.description,
                'checklist_status_id': active_id
            }
            status_poll.create(res)
        return {'type': 'ir.actions.act_window_close'}
