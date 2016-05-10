from openerp import api, exceptions, fields, models
from openerp import _
from openerp.exceptions import Warning

class ConfirmationWizard(models.TransientModel):
    _name="confirmation.wizard"
    
        # create a function that will save the info from your wizard into your model (active_id is the id of the record you called the wizard from, so you will save the info entered in wizard is that record)
    
    @api.multi
    def action_yes(self):

        return {
            'type': 'ir.actions.act_window_close',
        }
