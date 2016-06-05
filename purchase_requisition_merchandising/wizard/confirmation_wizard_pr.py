from openerp import api, exceptions, fields, models
from openerp import _
from openerp.exceptions import Warning

class ConfirmationWizardPr(models.TransientModel):
    _name="confirmation.wizard.pr"
    
        # create a function that will save the info from your wizard into your model (active_id is the id of the record you called the wizard from, so you will save the info entered in wizard is that record)
    
    @api.multi
    def action_yes(self):

        active_id = self._context.get('active_id', False)
#         indent_indent_obj = self.env['indent.indent'].search([('id', '=', active_id)])
        obj_PR = self.env['purchase.requisition'].browse(active_id)
        obj_PRL = self.env['purchase.requisition.line']
        line_data = obj_PRL.search([('requisition_id', '=', active_id)]).unlink()
        vals = {
                'bom_flag':True,
               'bom_flag1':False
               }
        obj_PR.write(vals)
        return {
            'type': 'ir.actions.act_window_close',
        }
