from odoo import api, fields, models, _


class HrEmpLeaveReport(models.AbstractModel):
    _name = 'report.letter_of_credit_report.template_letter_of_credit_report'

    @api.multi
    def render_html(self, docids, data=None):

        lc_pool = self.env['letter.credit'].search([('state', 'in', ('draft','open','confirmed','amendment','progress'))])

        lc_list = []
        for l in range(5):
            lc_obj = {}
            lc_obj['party_name'] = "MD-" + str(l)
            lc_obj['pr_date'] = "PR Date-" + str(l)
            lc_obj['pr_no'] = "PR No-" + str(l)
            lc_obj['lc_number'] = "LC-" + str(l)
            lc_obj['lc_date'] = "LC Date-" + str(l)
            lc_obj['ship_date'] = "Ship Date-" + str(l)
            lc_obj['exp_date'] = "Expire Date-" + str(l)
            lc_obj['initial_price'] = "Initial Price-" + str(l)
            lc_obj['amount'] = "Value-" + str(l)
            lc_obj['discharging_port'] = "Dis.Port-" + str(l)
            shipment_list = []
            for sN in range(0, 2):
                sh_obj = {}
                sh_obj['shipment_number'] = "Shipment-" + str(sN)
                sh_obj['etd'] = "ETD-" + str(sN)
                product_list = []
                for pN in range(0, 2):
                    p_obj = {}
                    p_obj['product_name'] = "Product-" + str(pN)
                    p_obj['qty'] = "Qty-" + str(pN)
                    p_obj['status'] = "Status-" + str(pN)
                    product_list.append(p_obj)
                sh_obj['product_list'] = product_list
                shipment_list.append(sh_obj)
            lc_obj['shipment_list'] = shipment_list
            lc_list.append(lc_obj)

        docargs = {
            'lists': lc_list


        }

        return self.env['report'].render('letter_of_credit_report.template_letter_of_credit_report', docargs)

