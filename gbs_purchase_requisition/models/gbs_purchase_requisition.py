from odoo import api, fields, models,_
from odoo.exceptions import ValidationError
from datetime import date
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    name = fields.Char(string='Purchase Requisition',default='/')
    department_id = fields.Many2one('hr.department',string='Department', store=True)
    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit', required=True,
                                        default=lambda self: self.env.user.default_operating_unit_id)
    region_type = fields.Selection([('local', 'Local'),('foreign', 'Foreign')], string="LC Region Type",help="Local: Local LC.\n""Foreign: Foreign LC.")
    purchase_by = fields.Selection([('cash', 'Cash'), ('credit', 'Credit'), ('lc', 'LC'), ('tt', 'TT')], string="Purchase By")
    requisition_date = fields.Date(string='Requisition Date',default = date.today())
    required_date = fields.Date(string='Required Date')
    state = fields.Selection([('draft', 'Draft'), ('in_progress', 'Confirmed'),
                              ('approve_head_procurement', 'Waiting For Approval'),('done', 'Approved'),
                              ('cancel', 'Cancelled')],'Status', track_visibility='onchange', required=True,
                             copy=False, default='draft')

    indent_ids = fields.Many2many('indent.indent','pr_indent_rel','pr_id','indent_id',string='Indent')
    attachment_ids = fields.One2many('ir.attachment', 'res_id', string='Attachments')

    @api.multi
    def action_in_progress(self):
        if not all(obj.line_ids for obj in self):
            raise UserError(_('You cannot confirm call because there is no product line.'))
        res = {
            'state': 'in_progress'
        }
        new_seq = self.env['ir.sequence'].next_by_code('purchase.requisition')

        if new_seq:
            res['name'] = new_seq

        self.write(res)

    @api.multi
    def action_open(self):
        self.write({'state': 'approve_head_procurement'})

    @api.multi
    def action_approve(self):
        res = self.env.ref('gbs_purchase_requisition.purchase_requisition_type_wizard')
        result = {
            'name': _('Please Select LC Region Type and Purchase By before approve'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'purchase.requisition.type.wizard',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
        }
        po_pool_obj = self.env['purchase.order'].search([('requisition_id','=',self.id)])
        if po_pool_obj:
            po_pool_obj.write({'check_po_action_button': True})
        return result

    @api.onchange('indent_ids')
    def indent_product_line(self):
        vals = []
        self.required_date = self.indent_ids.required_date
        for indent_id in self.indent_ids:
            indent_product_line_obj = self.env['indent.product.lines'].search([('indent_id','=',indent_id.id)])
            for indent_product_line in indent_product_line_obj:
                vals.append((0, 0, {'product_id': indent_product_line.product_id,
                                'name': indent_product_line.name,
                                'product_uom_id': indent_product_line.product_uom,
                                'product_qty': indent_product_line.product_uom_qty,
                          }))
                self.line_ids = vals

    ####################################################
    # ORM Overrides methods
    ####################################################

    def unlink(self):
        for indent in self:
            if indent.state != 'draft':
                raise ValidationError(_('You cannot delete in this state'))
            else:
                query = """ delete from ir_attachment where res_id=%s"""
                for att in self.attachment_ids:
                    self._cr.execute(query, tuple([att.res_id]))
                return super(PurchaseRequisition, self).unlink()


class PurchaseRequisitionLine(models.Model):
    _inherit = "purchase.requisition.line"

    product_ordered_qty = fields.Float('Ordered Quantities', digits=dp.get_precision('Product UoS'),
                                       default=1)
    name = fields.Text(string='Description')
    last_purchse_date = fields.Date(string='Last Purchase Date')
    last_qty = fields.Float(string='Last Purchase Qnty')
    last_product_uom_id = fields.Many2one('product.uom', string='Last Purchase Unit')
    last_price_unit = fields.Float(string='Last Unit Price')
    remark = fields.Char(string='Remarks')

    @api.onchange('product_id')
    def onchange_product_id(self):
        if not self.product_id:
            return {'value': {'product_ordered_qty': 1.0,
                              'product_uom_id': False,
                              'product_qty': 0.0,
                              'name': '',
                              'delay': 0.0
                              }
                    }
        # ..........................................
        if self.product_id:
            product_obj = self.env['product.product']
            product = product_obj.search([('id', '=', self.product_id.id)])
            product_name = product.name_get()[0][1]
            self.name = product_name
            self.product_uom = product.uom_id.id
            self.product_qty = product.qty_available
        if not self.account_analytic_id:
            self.account_analytic_id = self.requisition_id.account_analytic_id
        if not self.schedule_date:
            self.schedule_date = self.requisition_id.schedule_date

        # /////////////////////////////////////////


