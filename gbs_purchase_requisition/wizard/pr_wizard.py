from odoo import api, fields, models, _


class PurchaseRequisitionTypeWizard(models.TransientModel):
    _name = 'purchase.requisition.type.wizard'

    region_type = fields.Selection([('local', 'Local'), ('foreign', 'Foreign')],
                                   string="LC Region Type")

    purchase_by = fields.Selection([('cash', 'Cash'), ('credit', 'Credit'), ('lc', 'LC'), ('tt', 'TT')],
                                   string="Purchase By")

    @api.multi
    def save_type(self):
        form_id = self.env.context.get('active_id')
        pr_form_pool = self.env['purchase.requisition'].search([('id', '=', form_id)])
        pr_form_pool.write(
            {'region_type': self.region_type,'purchase_by': self.purchase_by,'state': 'done'})
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def cancel_window(self):
        form_id = self.env.context.get('active_id')
        pr_form_pool = self.env['purchase.requisition'].search([('id', '=', form_id)])
        pr_form_pool.write({'state': 'done'})
        return {'type': 'ir.actions.act_window_close'}










