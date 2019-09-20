from odoo import api, fields, models,_


class PurchaseRequisitionLine(models.Model):
    _inherit = "purchase.requisition.line"

    mrr_qty = fields.Float('MRR Qty')