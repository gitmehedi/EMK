from odoo import models, fields, api,_


class TDSRules(models.Model):
    _name = 'tds.challan.selection.wizard'
    _order = 'name desc'
    _description = 'TDS Challan Wizard'


    date_from = fields.Date(string='From Date', required=True)
    date_to = fields.Date(string='To Date', required=True)
    type = fields.Selection([
        ('both', 'BOTH'),
        ('vat', 'VAT'),
        ('tds', 'TDS'),
    ], string='Type', required=True,default= 'both')
    sub_operating_unit_id = fields.Many2one('sub.operating.unit', string='Operating Unit')
    supplier_id = fields.Many2one('res.partner', string="Supplier")

    @api.multi
    def generate_action(self):
        print "---------"
