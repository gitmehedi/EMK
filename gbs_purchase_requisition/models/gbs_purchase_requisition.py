from odoo import api, fields, models,_
from odoo.exceptions import ValidationError
from datetime import date


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    department_id = fields.Many2one('hr.department',
                                    string='Department', store=True)
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
    # attachment_ids = fields.One2many('purchase.requisition.attachments', 'pr_id', string='Attachments')
    attachment_ids = fields.Many2many('ir.attachment', 'ir_att_pr_rel', 'pr_id', 'ir_att_id', string='Attachment')

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
        # self.write({'state': 'done'})
        return result

    @api.onchange('indent_ids')
    def indent_product_line(self):
        vals = []
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

        return super(PurchaseRequisition, self).unlink()


class PurchaseRequisitionLine(models.Model):
    _inherit = "purchase.requisition.line"

    name = fields.Text(string='Description')
    last_purchse_date = fields.Date(string='Last Purchase Date')
    last_qty = fields.Float(string='Last Purchase Qnty')
    last_product_uom_id = fields.Many2one('product.uom', string='Last Purchase Unit')
    last_price_unit = fields.Float(string='Last Unit Price')
    remark = fields.Char(string='Remarks')


# class PurchaseRequisitionAttachments(models.Model):
#     _name = 'purchase.requisition.attachments'
#     _description = 'Purchase Requisition Attachments'
#
#     title = fields.Char(string='Title', required=True)
#     file = fields.Binary(default='Attachment', required=True)
#     pr_id = fields.Many2one('purchase.requisition', string='LC Number')
