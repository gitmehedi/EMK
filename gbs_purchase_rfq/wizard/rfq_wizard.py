from datetime import datetime, date
from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError


class RFQWizard(models.TransientModel):
    _name = 'rfq.wizard'

    def _get_default_operating_unit(self):
        op_ids = [i.operating_unit_id.id for i in self.env['purchase.requisition'].search([('id','in',self.env.context.get('active_ids'))])]
        if (len(set(op_ids)) == 1):
            return op_ids[0]
        else:
            raise UserError(_('Operating unit must be same.'))

    product_lines = fields.One2many('rfq.product.line.wizard', 'rfq_id', string='Product(s)')

    pr_ids = fields.Many2many('purchase.requisition', string='Purchase Requisition',
                                  default=lambda self: self.env.context.get('active_ids'))
    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit',
                                        default=_get_default_operating_unit)

    @api.multi
    @api.onchange('operating_unit_id')
    def _onchange_operating_unit(self):
        for wiz in self:
            if wiz.operating_unit_id:
                return {'domain': {'pr_ids': [('operating_unit_id', '=', wiz.operating_unit_id.id),('state','=','done')]}}
            else:
                wiz.pr_ids = []

    @api.onchange('pr_ids')
    def _onchange_pr_ids(self):
        if self.pr_ids:
            vals = []
            # form_ids = self.env.context.get('active_ids')
            line_pool = self.env['purchase.requisition.line'].search([('requisition_id', 'in', self.pr_ids.ids)])
            for obj in line_pool:
                # product_qty = obj.product_qty - obj.product_received_qty
                # if product_qty > 0:
                vals.append((0, 0, {'product_id': obj.product_id,
                                    'product_qty': obj.product_ordered_qty,
                                    'product_uom_id': obj.product_uom_id.id,
                                    'price_unit': obj.price_unit,
                                    }))
            self.product_lines = vals
        else:
            self.product_lines = []

    @api.multi
    def print_rfq(self):
        data = {}
        vals = []
        for obj in self.product_lines:
            vals.append(({  'product_id': obj.product_id.name,
                            'product_qty': obj.product_qty,
                            'product_uom_id': obj.product_uom_id.name,
                        }))
        data['vals'] = vals

        return self.env['report'].get_action(self, 'gbs_purchase_rfq.rfq_report', data=data)

    @api.multi
    def action_save_rfq(self):
        rfq_obj = self.env['purchase.rfq']
        rfq_line_obj = self.env['purchase.rfq.line']
        rfq_date = datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        rfq_id = False

        if not self.product_lines:
            raise UserError(_('Unable to RFQ without product. Please add product(s).'))

        rfq_name = self.env['ir.sequence'].next_by_code_new('purchase.rfq', date.today(),
                                                           self.operating_unit_id) or '/'

        res_order = {
            'name': rfq_name,
            'operating_unit_id': self.operating_unit_id.id,
            'company_id': self.env.user.company_id.id,
            'responsible': self.env.user.id,
            'rfq_date': rfq_date,
            'pr_ids': [(6, 0, self.pr_ids.ids)],
        }

        rfq = rfq_obj.create(res_order)
        if rfq:
            rfq_id = rfq.id

        product_list = []
        for obj in self.product_lines:
            if obj.product_id not in product_list:
                product_list.append(obj.product_id)

        list_new = self.product_lines
        new_list = []
        for obj in product_list:
            count = 0
            qty = 0
            for ele in list_new:
                if obj == ele.product_id:
                    count += 1
                    qty += ele.product_qty
                    if count == 1:
                        new_list.append(ele)
            for att in new_list:
                if obj == att.product_id:
                    att.product_qty = qty

        rfq_line_ids = []
        for line in new_list:
            res_order_line = {
                'product_id': line.product_id.id,
                'product_qty': line.product_qty,
                'price_unit': line.price_unit,
                'product_uom_id': line.product_uom_id.id,
                'rfq_id': rfq_id,
            }
            rfq_line_obj = rfq_line_obj.create(res_order_line)
            rfq_line_ids.append(rfq_line_obj)


        for pr_id in self.pr_ids:
            for rfq_line_id in rfq_line_ids:
                pr_line_id = pr_id.line_ids.filtered(lambda x: x.product_id.id == rfq_line_id.product_id.id)
                if pr_line_id:
                    self._cr.execute('INSERT INTO pr_rfq_line_rel (pr_line_id,rfq_line_id) VALUES (%s, %s)',
                                     tuple([pr_line_id.id, rfq_line_id.id]))

        view_id = self.env.ref('gbs_purchase_rfq.view_purchase_rfq_form')

        return {
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id and view_id.id or False,
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.rfq',
            'res_id': rfq_id,
            'target': 'current',
        }


class RFQProductLineWizard(models.TransientModel):
    _name = 'rfq.product.line.wizard'

    rfq_id = fields.Many2one('rfq.wizard', string='RFQ', ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', required=True, ondelete='cascade')
    product_qty = fields.Float(string='Quantity')
    price_unit = fields.Float(related='product_id.standard_price',string='Price Unit')
    product_uom_id = fields.Many2one(related='product_id.uom_id',comodel='product.uom', string='Unit of Measure')
