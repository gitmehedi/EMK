# imports of odoo
from odoo import api, fields, models, _


class MrpBomWizard(models.TransientModel):
    _name = 'mrp.bom.wizard'

    historical_date = fields.Date(string='Historical Date', required=True)

    @api.multi
    def action_save(self):
        bom_id = self.env.context.get('active_id')
        MRP_BOM = self.env['mrp.bom']
        bom = MRP_BOM.search([('id', '=', bom_id)])

        return bom.action_create_new_version(self.historical_date)
