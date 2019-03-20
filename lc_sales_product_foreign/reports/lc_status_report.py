from odoo import api, models
from odoo.tools.misc import formatLang


class PurchaseSummaryReport(models.AbstractModel):
    _name = 'report.lc_sales_product_foreign.lc_status_foreign_template'
    sql_str = """ """

    @api.multi
    def render_html(self, docids, data=None):
        lc_pool = self.env['letter.credit'].search([('state','=',data['status']),('type','=','export'),('region_type','=','foreign')])
        data = {
            'product_id': data['product_id'],
            'pur_month': data['month'],
            'pur_year': data['year'],
            'status' :  data['status'],

        }
        lc_list= []
        for lc in lc_pool:
            list_obj = {
                'lc_name': lc.name,
                'lc_date': lc.issue_date,
                'first_party': lc.second_party_applicant.name,
                'lc_qty': lc.second_party_applicant.name,
                'pi_no': lc.second_party_applicant.name,
                'pi_date': lc.second_party_applicant.name,
                'delivery_qty': lc.second_party_applicant.name,
                'pending_qty': lc.second_party_applicant.name,
                'lst_sp_date': lc.shipment_date,
                'lc_expiry_date': lc.expiry_date,
            }
            lc_list.append(list_obj)

        docargs = {
            'data': data,
            'lc_list': lc_list,
        }

        return self.env['report'].render('lc_sales_product_foreign.lc_status_foreign_template', docargs)