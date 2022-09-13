from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError

class LCReceivablePayment(models.Model):
    _inherit = 'lc.receivable.payment'

    @api.model
    def create(self, vals):
        purchase_shipment = self.env['purchase.shipment'].search([('lc_id', '=', vals['lc_id'])])
        if purchase_shipment:
            exit_shipment = [i for i in purchase_shipment if i.id == vals['shipment_id']]
        if not exit_shipment or not purchase_shipment:
            raise UserError(_('Please select a valid shipment'))

        # get pi
        query = ("select pi_id from pi_lc_rel where lc_id={0}").format(vals['lc_id'])
        self.env.cr.execute(query)
        pi_ids = self.env.cr.dictfetchall()
        pi_ids_val = []
        invoice_ids = []
        for pi in pi_ids:
            pi_ids_val.append(pi['pi_id'])

        so_objs = self.env['sale.order'].search([('pi_id', 'in', pi_ids_val)])
        if so_objs:
            for so_obj in so_objs:
                for invoice_id in so_obj.invoice_ids:
                    invoice_ids.append(invoice_id.id)

        paym_invoice_ids = vals['invoice_ids'][0][2]
        exit_inv = True
        for invoice_id in paym_invoice_ids:
            if invoice_id not in invoice_ids:
                exit_inv = False
        if not exit_inv:
            raise UserError(_('Please select valid invoices'))

        return super(LCReceivablePayment, self).create(vals)

    @api.multi
    def write(self, vals):
        return super(LCReceivablePayment, self).write(vals)