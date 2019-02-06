from odoo import models, fields, api,_


class TDSChallaSelectionWizard(models.TransientModel):
    _name = 'tds.challan.selection.wizard'
    _description = 'TDS Challan Wizard'


    date_from = fields.Date(string='From Date', required=True)
    date_to = fields.Date(string='To Date', required=True)
    type = fields.Selection([
        ('both', 'BOTH'),
        ('vat', 'VAT'),
        ('tds', 'TDS'),
    ], string='Type', required=True,default= 'both')
    operating_unit_id = fields.Many2one('operating.unit', string='Branch')
    supplier_id = fields.Many2one('res.partner', string="Supplier")

    @api.multi
    def generate_action(self):
        res_view = self.env.ref('tds_vendor_challan.view_tds_acc_move_line_tree')

        selection_type = []
        if self.type == 'both':
            selection_type = ['vat','tds']
        else:
            selection_type.append(self.type)

        vals = [('tax_type', 'in', selection_type),('is_deposit','=',False),
                 ('date', '<=', self.date_to),('date', '>=', self.date_from)]

        if self.supplier_id:
            vals.append(('partner_id','=',self.supplier_id.id))

        if self.operating_unit_id:
            vals.append(('operating_unit_id','=',self.operating_unit_id.id))

        result = {
            'name': _('Pending Challan'),
            'view_type': 'form',
            'view_mode': 'tree',
            'view_id': res_view and res_view.id or False,
            'res_model': 'account.move.line',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'account.action_view_account_move_line_reconcile' : False,
            'target': 'current',
            'domain': vals,
        }
        return result
