from odoo import models, fields, api,_
from odoo.exceptions import UserError,ValidationError


class TDSChallaSelectionWizard(models.TransientModel):
    _name = 'tds.challan.selection.wizard'
    _description = 'TDS Challan Wizard'


    date_from = fields.Date(string='From Date', required=True,
                            default=lambda self: self.env.context.get('from_date'))
    date_to = fields.Date(string='To Date', required=True,
                          default=lambda self: self.env.context.get('to_date'))
    type = fields.Selection([
        ('tds', 'TDS'),
        ('vat', 'VAT'),
    ], string='Type', required=True,readonly=True,default=lambda self: self.env.context.get('tax_type'))
    operating_unit_id = fields.Many2one('operating.unit', string='Branch')
    supplier_id = fields.Many2one('res.partner', string="Vendor")
    product_ids = fields.Many2many('product.product', string='Product', required=True,
                                   default=lambda self: self.env.context.get('product_ids'))

    @api.constrains('date_from','date_to')
    def _check_date(self):
        if self.date_from > self.date_to:
            raise ValidationError(
                "Please Check End Date!! \n 'End Date' must be greater than 'From Date'")
        if self.date_from < self.env.context.get('from_date'):
            raise ValidationError(
                "No record found. Please select date after '%'."% self.env.context.get('from_date'))
        if self.date_to < self.env.context.get('to_date'):
            raise ValidationError(
                "No record found. Please select date before '%'." % self.env.context.get('to_date'))


    @api.onchange('product_ids')
    def _onchange_product_ids(self):
        if self.product_ids:
            self.supplier_id = []
            self.operating_unit_id = []
            move_lines = self.env['account.move.line'].search(
                [('id', 'in', self.env.context.get('records')),('product_id','in',self.product_ids.ids)])
            if move_lines:
                supplier_ids = [move.partner_id.id for move in move_lines]
                operating_unit_ids = [move.operating_unit_id.id for move in move_lines]
                return {'domain': {
                    'supplier_id': [('id', 'in', supplier_ids)],
                    'operating_unit_id': [('id', 'in', operating_unit_ids)],
                }}


    @api.multi
    def generate_action(self):
        vals = [('id','in',self.env.context.get('records')),
                ('tax_type', '=', self.type),
                ('date', '<=', self.date_to),('date', '>=', self.date_from)]

        if self.supplier_id:
            vals.append(('partner_id','=',self.supplier_id.id))

        if self.operating_unit_id:
            vals.append(('operating_unit_id','=',self.operating_unit_id.id))


        # find final move lines to generate challan
        move_lines = self.env['account.move.line'].search(vals)

        if not move_lines:
            raise ValidationError("No record found.")

        res_view = self.env.ref('tds_vat_challan.tds_vat_challan_form_view')

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
                        'name': self.type.upper()+' Challan['+self.date_from+' to '+self.date_to+']',
                        'currency_id': self.env.user.company_id.currency_id.id,
                        },
        }
        return result

