from odoo import api, fields, models, _

class StockIndent(models.Model):
    _inherit = 'indent.indent'

    check_pr_issued = fields.Boolean(compute='_compute_pr_issued', string='Check PR Issued')

    @api.multi
    def _compute_pr_issued(self):
        for indent in self:
            pool_pr_obj = self.env['purchase.requisition'].sudo().search([('indent_ids', '=', indent.id)])
            if pool_pr_obj:
                query = """SELECT 
                                    product_id,sum(product_ordered_qty) as ordered_qty  
                               FROM 
                                    purchase_requisition_line 
                               WHERE requisition_id IN %s 
                               GROUP BY product_id;"""
                self._cr.execute(query, tuple([tuple(pool_pr_obj.ids)]))
                for (product_id, ordered_qty) in self.env.cr.fetchall():
                    pool_indent_pro_obj = indent.product_lines.search(
                        [('product_id', '=', product_id), ('indent_id', '=', self.id)])
                    if ordered_qty >= pool_indent_pro_obj.product_uom_qty:
                        indent.check_pr_issued = False
                    else:
                        indent.check_pr_issued = True
                        break
                if indent.check_pr_issued == False:
                    indent.write({'pr_indent_check': False})
            else:
                indent.check_pr_issued = True

    @api.multi
    def action_view_purchase_requisition(self):
        res = self.env.ref('purchase_requisition.view_purchase_requisition_form')
        purchase_req = self._create_purchase_req()
        if purchase_req:
            self._create_purchase_req_line(purchase_req[0].id or False)
        result = {
            'name': _('PR'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'purchase.requisition',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'res_id': purchase_req[0].id
        }
        query = """ INSERT INTO pr_indent_rel (pr_id,indent_id)VALUES (%s, %s) """
        self._cr.execute(query, tuple([purchase_req[0].id, self.id]))
        return result

    @api.multi
    def _create_purchase_req(self):
        pur_req_obj = self.env['purchase.requisition']

        values = {
            'user_id': self.env.user.id,
            'operating_unit_id': self.operating_unit_id.id,
            'required_date': self.required_date,
            'picking_type_id': self.picking_type_id.id,
            'company_id': self.company_id.id,
            'dept_location_id': self.stock_location_id.id,
        }

        return pur_req_obj.create(values)

    @api.multi
    def _create_purchase_req_line(self, req_id):
        pur_line_obj = self.env['purchase.requisition.line']

        for product_line in self.product_lines:
            values = {
                'requisition_id': req_id,
                'product_id': product_line.product_id.id,
                'name': product_line.name or False,
                'product_qty': product_line.qty_available or False,
                'product_uom_id': product_line.product_uom.id or False,
                'product_ordered_qty': product_line.product_uom_qty - product_line.received_qty  or False,
                'schedule_date': self.required_date or False,
                'remark': product_line.remarks or False,
            }
            pur_line_obj.create(values)