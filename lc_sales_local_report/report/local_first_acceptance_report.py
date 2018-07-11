import datetime
from odoo import fields,api, models

class LocalFirstAcceptanceReport(models.AbstractModel):
    _name = 'report.lc_sales_local_report.local_first_acceptance_temp'

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
            'lines': get_data['acceptances'],
            'address': data['address'],

        }
        return self.env['report'].render('lc_sales_local_report.local_first_acceptance_temp', docargs)

    def get_report_data(self, data):
        acceptances = []
        current_date =  fields.Date.context_today(self)
        currency_format = '9,99,99,99,999'

        product_temp_id = data['product_temp_id']

        sql_in_tk = '''SELECT DISTINCT pt.id as template_id,
                              lc.id as lc_id,
                              ps.id as shipment_id,
                              pt.name as product_name,
                              ps.name as shipment_name,
                              lc.name as lc_name, 
                              to_char(ps.invoice_value, '%s') as value,
                              rp.name as customer,
                              lc.tenure as tenor,
                              lc.second_party_bank as customer_bank,
                              rb.name as beneficiary_bank,
                              ps.to_sales_date as dispatch_to_sale,
                              ps.to_buyer_date as dispatch_to_customer,
                              ps.comment as comment,
                              rc.symbol as currency,
                              (CASE
                                  WHEN ps.to_buyer_date is not null THEN date('%s') - date(ps.to_buyer_date)
                                  WHEN ps.to_sales_date is not null THEN date('%s') - date(ps.to_sales_date)
                                ELSE 0
                              END) as aging
                       FROM product_template pt
                          right join product_product pp on pp.product_tmpl_id = pt.id
                          right join shipment_product_line sp on pp.id = sp.product_id
                          left join purchase_shipment ps on ps.id = sp.shipment_id
                          left join letter_credit lc on lc.id = ps.lc_id
                          left join res_partner rp on lc.second_party_applicant = rp.id
                          left join res_bank rb on lc.first_party_bank = rb.id
                          left join res_currency rc on lc.currency_id = rc.id
                       WHERE pt.id = %s and lc.type = 'export' and lc.region_type = 'local' and ps.state in ('to_sales','to_buyer')
                       ORDER by pt.id asc
                    '''% (currency_format,current_date,current_date,product_temp_id)

        self.env.cr.execute(sql_in_tk)
        for vals in self.env.cr.dictfetchall():
            if vals:
                acceptances.append(vals)

        return {'acceptances': acceptances}
