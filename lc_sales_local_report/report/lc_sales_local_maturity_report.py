from odoo import fields,api, models
from odoo.tools.misc import formatLang

class LCSalesMaturityReport(models.AbstractModel):
    _name = 'report.lc_sales_local_report.lc_sales_maturity_temp'

    @api.multi
    def render_html(self, docids, data=None):

        get_data = self.get_report_data(data)
        report_utility_pool = self.env['report.utility']
        op_unit_obj = self.env.user.default_operating_unit_id
        data['address'] = report_utility_pool.getAddressByUnit(op_unit_obj)

        docargs = {
            'doc_ids': self._ids,
            'docs': self,
            'record': data,
            'lines': get_data['data_list'],
            'address': data['address'],
            'total': get_data['total'],

        }
        return self.env['report'].render('lc_sales_local_report.lc_sales_maturity_temp', docargs)

    def get_report_data(self, data):
        data_list = []
        product_temp_id = data['product_temp_id']

        total_value = {
            'title': 'TOTAL VALUE',
            'total_val': 0,
        }

        sql_in_tk = '''SELECT DISTINCT pt.id as template_id,
                              lc.id as lc_id,
                              ps.id as shipment_id,
                              pt.name as product_name,
                              ps.name as shipment_name,
                              lc.unrevisioned_name as lc_name, 
                              COALESCE((ps.invoice_value),0) as value,
                              rp.name as customer,
                              lc.tenure as tenor,
                              lc.second_party_bank as customer_bank,
                              rb.bic as beneficiary_bank,
                              rc.symbol as currency,
                              ps.to_maturity_date,
                              ps.bill_id as bill_id
                       FROM product_template pt
                          JOIN product_product pp on pp.product_tmpl_id = pt.id
                          JOIN shipment_product_line sp on pp.id = sp.product_id
                          JOIN purchase_shipment ps on ps.id = sp.shipment_id
                          JOIN letter_credit lc on lc.id = ps.lc_id
                          LEFT JOIN res_partner rp on lc.second_party_applicant = rp.id
                          LEFT JOIN res_partner_bank bank_acc on lc.first_party_bank_acc = bank_acc.id
                          LEFT JOIN res_bank rb on bank_acc.bank_id = rb.id
                          LEFT JOIN res_currency rc on lc.currency_id = rc.id
                       WHERE pt.id = %s AND lc.type ='export' AND lc.region_type = 'local' AND ps.state = 'to_maturity'
                       ORDER BY pt.id ASC
                    '''% (product_temp_id)

        self.env.cr.execute(sql_in_tk)
        for vals in self.env.cr.dictfetchall():
            if vals:
                total_value['total_val'] = total_value['total_val'] + vals['value']
                vals['value'] = formatLang(self.env, vals['value']) if vals['value'] else None
                data_list.append(vals)

        total_value['total_val'] = formatLang(self.env, total_value['total_val']) if total_value['total_val'] else None
        return {'data_list': data_list ,'total': total_value}