from odoo import models, fields, api,_


class TDSChallaOUSelectionWizard(models.TransientModel):
    _name = 'tds.challan.ou.selection.wizard'
    _description = 'TDS Challan Operating Unit Wizard'


    sub_operating_unit_id = fields.Many2one('sub.operating.unit', string='Operating Unit')
