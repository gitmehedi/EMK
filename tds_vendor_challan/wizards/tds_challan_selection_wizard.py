from odoo import models, fields, api,_


class TDSRules(models.Model):
    _name = 'tds.challan.selection.wizard'
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
        res_view = self.env.ref('tds_vendor_challan.view_tds_acc_move_line_tree')

        # self.date_from,self.date_to
        selection_type = []
        if self.type == 'both':
            selection_type = ['vat','tds']
        else:
            selection_type.append(self.type)

        result = {
            'name': _('List'),
            'view_type': 'form',
            'view_mode': 'tree',
            'view_id': res_view and res_view.id or False,
            'res_model': 'account.move.line',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'domain': [('tax_type', 'in', selection_type),('is_deposit','=',False)],
        }

        return result
