from openerp import models, fields, api, exceptions
from openerp.osv import osv


class ConfigureEmpChecklist(models.Model):
    _name = "hr.checklist.generate.popup"

    checklist_item_ids= fields.Many2many('hr.exit.checklist.item')

    @api.multi
    def compute_sheet(self, vals):
        line_pool = self
        #active_id = vals['active_id']
        #checklist_pool = self.env['hr.configure.emp.checklists']
        #line_pool = self.env['hr.exit.configure.checklists.line']
        item_pool = self.env['hr.exit.checklist.item']
        status_poll = self.env['hr.checklist.status']
        line_ids = []

        #data = self

        if not self.checklist_item_ids:
            raise osv.except_osv(_("Warning!"), _("You must select items to generate checklist"))
        for item in self.browse(self['checklist_item_ids']):
        #for item in self.checklist_item_ids:
            # line_data = line_pool.onchange_employee_id(cr, uid, [], from_date, to_date, emp.id, contract_id=False,
            #                                            context=context)
            res = {
                'checklist_item_id': item.id.id,
                'item_description':item.id.checklist_type.id,
                # 'check_list_type_id': item.checklist_type,
                # 'checklist_item_ids': item.checklist_item_id
            }
            status_poll.create(res)
        #line_pool.compute_sheet(line_ids)
        return {'type': 'ir.actions.act_window_close'}
