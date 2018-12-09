from odoo import api, fields, models,_
from odoo.exceptions import UserError, ValidationError

class LCPO(models.Model):
    _inherit = "letter.credit"

    po_ids = fields.Many2many('purchase.order', 'po_lc_rel', 'lc_id', 'po_id', string='Purchase Order')
    product_lines = fields.One2many('lc.product.line', 'lc_id', string='Product(s)')

    @api.onchange('po_ids')
    def po_product_line(self):
        self.product_lines = []
        vals = []
        self.first_party = None
        self.second_party_beneficiary = None
        self.currency_id = None
        self.lc_value = None
        self.operating_unit_id = None
        for po_id in self.po_ids:
            self.first_party = po_id.company_id.id
            self.second_party_beneficiary = po_id.partner_id.id
            self.currency_id = po_id.currency_id.id
            self.lc_value += po_id.amount_total
            self.operating_unit_id = po_id.operating_unit_id.id
            for obj in po_id.order_line:
                vals.append((0, 0, {'product_id': obj.product_id,
                                    'name': obj.name,
                                    'product_qty': obj.product_qty,
                                    'price_unit': obj.price_unit,
                                    'currency_id': obj.currency_id,
                                    'date_planned': obj.date_planned,
                                    'product_uom':obj.product_uom
                                    }))
        self.product_lines = vals

    @api.multi
    @api.constrains('operating_unit_id')
    def _check_operating_unit_id(self):
        for po in self.po_ids:
            if self.operating_unit_id.id != po.operating_unit_id.id:
                raise ValidationError(_("Operating unit of %s is not same with operating unit of letter of credit.\n"
                                        "Your purchase order's operating unit and letter of credit's operating unit must be same.") % (
                                      po.name))

    @api.multi
    @api.constrains('po_ids')
    def _check_po_ids(self):
        if self.type == 'import':
            for compare_po in self.po_ids:
                for po in self.po_ids:
                    if compare_po.company_id.id != po.company_id.id:
                        raise ValidationError(_("Applicant mismatch. Applicant name must be same."))
                    if compare_po.partner_id.id != po.partner_id.id:
                        raise ValidationError(_("Supplier mismatch. Supplier name must be same."))
                    if compare_po.currency_id.id != po.currency_id.id:
                        raise ValidationError(_("Currency mismatch. Currency must be same."))
                    if compare_po.operating_unit_id.id != po.operating_unit_id.id:
                        raise ValidationError(_("Unit mismatch. Unit must be same."))
