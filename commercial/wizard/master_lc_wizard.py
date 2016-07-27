from openerp import api, exceptions, fields, models
from openerp.addons.helper import validator

class MasterLCWizard(models.TransientModel):
    """
    Product Style Amendment Wizard
    """
    _name = "master.lc.wizard"

    @api.multi
    def amaendment_copy(self, context=None):

        obj = self.env['master.lc'].browse(context['active_id'])
        res = obj.extend_copy(context)

        
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'src_model': 'master.lc',
            'res_model': 'master.lc',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'res_id': res.id
        }
       
       
