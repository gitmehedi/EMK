from odoo import models, fields, api,_
from odoo.exceptions import UserError,ValidationError


class TDSChallaSelectionWizard(models.TransientModel):
    _name = 'tds.challan.selection.wizard'
    _description = 'TDS Challan Wizard'

    type = fields.Selection([
        ('tds', 'TDS'),
        ('vat', 'VAT'),
    ], string='Type', required=True,default='tds')
    operating_unit_id = fields.Many2one('operating.unit', string='Branch')
    supplier_ids = fields.Many2many('res.partner', string="Vendor")
    product_ids = fields.Many2many('product.product', string='Product')

    @api.constrains('date_from','date_to')
    def _check_date(self):
        if self.date_from > self.date_to:
            raise ValidationError(
                "Please Check End Date!! \n 'End Date' must be greater than 'From Date'")


    @api.onchange('product_ids')
    def _onchange_product_ids(self):
        type = self.type
        if not type:
            warning = {
                    'title': _('Warning!'),
                    'message': _('You must first select a Type(TDS/VAT)!'),
                }
            return {'warning': warning}


    @api.onchange('supplier_ids')
    def _onchange_supplier_ids(self):
        type = self.type
        if not type:
            warning = {
                'title': _('Warning!'),
                'message': _('You must first select a Type(TDS/VAT)!'),
            }
            return {'warning': warning}


    @api.multi
    def generate_action(self):
        vals = [('tax_type', '=', self.type),
                ('is_paid', '=', True),
                ('is_challan', '=', False)]

        if self.supplier_ids:
            vals.append(('partner_id','in',self.supplier_ids.ids))

        if self.product_ids:
            vals.append(('product_id','in',self.product_ids.ids))

        if self.operating_unit_id:
            vals.append(('operating_unit_id','=',self.operating_unit_id.id))

        # find final move lines to generate challan
        move_lines = self.env['account.move.line'].search(vals)

        if not move_lines:
            raise ValidationError("No record found.")

        res_view = self.env.ref('tds_vat_challan.tds_vat_challan_form_view')

        if self.type == 'tds':
            pre_name = 'MTB-TC'
        else:
            pre_name = 'MTB-VC'

        result = {
            'name': _('Challan Item'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res_view and res_view.id or False,
            'res_model': 'tds.vat.challan',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'context': {'acc_move_line_ids': move_lines.ids,
                        'name': pre_name+'-'+fields.Date.context_today(self),
                        'currency_id': self.env.user.company_id.currency_id.id,
                        'type': self.type,
                        },
        }
        return result


# date_from = fields.Date(string='From Date', required=True)
# date_to = fields.Date(string='To Date', required=True)
# ('date', '<=', self.date_to), ('date', '>=', self.date_from)
#  if self.product_ids:
#     self.supplier_id = []
#     self.operating_unit_id = []
#     move_lines = self.env['account.move.line'].search(
#         [('id', 'in', self.env.context.get('records')),('product_id','in',self.product_ids.ids)])
#     if move_lines:
#         supplier_ids = [move.partner_id.id for move in move_lines]
#         operating_unit_ids = [move.operating_unit_id.id for move in move_lines]
#         return {'domain': {
#             'supplier_id': [('id', 'in', supplier_ids)],
#             'operating_unit_id': [('id', 'in', operating_unit_ids)],
#         }}