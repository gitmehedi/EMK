from datetime import datetime
from odoo import api, fields, models,_


class PurchaseRFQ(models.Model):
    _name = "purchase.rfq"
    _description = "Request For Quotation"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'rfq_date desc'

    name = fields.Char('RFQ Reference', required=True,readonly=True,index=True, copy=False, default='New')
    pr_ids = fields.Many2many(comodel_name='purchase.requisition',string='Purchase Requisition',readonly=True)
    operating_unit_id = fields.Many2one(comodel_name='operating.unit',string='Operating Unit',readonly=True,
                                        default=lambda self: self.env.user.default_operating_unit_id,
                                        track_visibility='onchange',required=True)
    rfq_date = fields.Datetime(string='Date of Request', default = datetime.now(), readonly=True,
                               track_visibility='onchange', required=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True,
                                 default=lambda self: self.env.user.company_id, required=True)
    responsible = fields.Many2one('res.users', string='Responsible', required=True, readonly=True,
                                  default=lambda self: self.env.user,track_visibility='onchange')
    purchase_rfq_lines = fields.One2many('purchase.rfq.line', 'rfq_id', string='Product(s)')
    order_count = fields.Integer(compute='_compute_orders_number', string='Number of Orders')

    @api.multi
    def _compute_orders_number(self):
        for rfq in self:
            purchase_ids = self.env['purchase.order'].search([('rfq_id','=',rfq.id)])
            rfq.order_count = len(purchase_ids)

    @api.multi
    def confirm_for_mail(self):
        res = self.env.ref('gbs_purchase_rfq.rfq_email_template_wizard')

        vals = []
        for obj in self.purchase_rfq_lines:
            vals.append(({'product_id': obj.product_id.name,
                          'product_qty': obj.product_qty,
                          'product_uom_id': obj.product_uom_id.name,
                          }))

        result = {
            'name': _('Send RFQ'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'rfq.email.template.wizard',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'context': {
                'vals': vals,
            },
        }

        return result

    @api.multi
    def print_rfq(self):
        data = {}
        vals = []
        for obj in self.purchase_rfq_lines:
            vals.append(({'product_id': obj.product_id.name,
                          'product_qty': obj.product_qty,
                          'product_uom_id': obj.product_uom_id.name,
                          }))
        data['vals'] = vals

        return self.env['report'].get_action(self, 'gbs_purchase_rfq.rfq_report', data=data)



class RFQProductLineWizard(models.Model):
    _name = 'purchase.rfq.line'

    rfq_id = fields.Many2one('purchase.rfq', string='RFQ Id', ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', required=True, ondelete='cascade')
    product_qty = fields.Float(string='Required Qty')
    po_receive_qty = fields.Float(string='PO Qty')
    due_qty = fields.Float(string='Due Qty',compute='_compute_due_qty')
    price_unit = fields.Float(related='product_id.standard_price',string='Price Unit', store=True)
    product_uom_id = fields.Many2one(related='product_id.uom_id',comodel='product.uom',
                                     string='Unit of Measure', store=True)

    pr_line_ids = fields.Many2many('purchase.requisition.line', 'pr_rfq_line_rel', 'rfq_line_id', 'pr_line_id', 'PR ids')

    @api.depends('product_qty', 'po_receive_qty')
    def _compute_due_qty(self):
        for line in self:
            if line.product_qty and line.po_receive_qty:
                diff = line.product_qty - line.po_receive_qty
                if diff>0:
                    line.due_qty = diff
                else:
                    line.due_qty = 0.0
            else:
                line.due_qty = line.product_qty

