# imports of odoo
from odoo import models, fields, api, _
from odoo.exceptions import Warning


class PurchaseRequisition(models.Model):
    _inherit = "purchase.requisition"

    @api.multi
    def action_confirm(self):
        self.ensure_one()

        if len(self.purchase_ids) > 0:
            raise Warning(_('You can not reset to confirm state due to have quotation using this PR.'))

        sql_str = """SELECT
                        r.id
                    FROM 
                        purchase_rfq r
                        JOIN purchase_requisition_purchase_rfq_rel l ON l.purchase_rfq_id = r.id
                    WHERE
                        l.purchase_requisition_id=%s
        """

        self.env.cr.execute(sql_str, (self.id,))
        purchase_rfq_ids = self.env.cr.fetchall()
        if len(purchase_rfq_ids) > 0:
            raise Warning(_('You can not reset to confirm state due to have RFQ using this PR.'))

        # sql_str = """SELECT
        #                 o.id AS purchase_order_id
        #             FROM
        #                 purchase_order o
        #                 JOIN purchase_rfq r ON r.id = o.rfq_id
        #                 JOIN purchase_requisition_purchase_rfq_rel l ON l.purchase_rfq_id = r.id
        #             WHERE
        #                 l.purchase_requisition_id=%s"""
        # self.env.cr.execute(sql_str, (self.id,))
        # purchase_order_ids = self.env.cr.fetchall()
        # if len(purchase_order_ids) > 0:
        #     raise Warning(_('You can not reset to confirm state due to have quotation using this PR through RFQ.'))

        self.write({'state': 'in_progress'})
