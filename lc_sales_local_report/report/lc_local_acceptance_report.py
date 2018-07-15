from odoo import fields,api, models
from odoo.tools.misc import formatLang

class LocalFirstAcceptanceReport(models.AbstractModel):
    _name = 'report.lc_sales_local_report.local_first_acceptance_temp'

    @api.multi
    def render_html(self, docids, data=None):

        state_condition = 'to_sales','to_buyer'
        acceptance_utility_pool = self.env['acceptance.report.utility']
        get_data = acceptance_utility_pool.get_report_data(data,state_condition)
        report_utility_pool = self.env['report.utility']
        op_unit_obj = self.env.user.default_operating_unit_id
        data['address'] = report_utility_pool.getAddressByUnit(op_unit_obj)

        docargs = {
            'doc_ids': self._ids,
            'docs': self,
            'record': data,
            'lines': get_data['acceptances'],
            'address': data['address'],
            'total': get_data['total'],

        }
        return self.env['report'].render('lc_sales_local_report.local_first_acceptance_temp', docargs)

class LocalSecondAcceptanceReport(models.AbstractModel):
    _name = 'report.lc_sales_local_report.local_second_acceptance_temp'

    @api.multi
    def render_html(self, docids, data=None):

        state_condition = 'to_seller_bank','to_buyer_bank'
        acceptance_utility_pool = self.env['acceptance.report.utility']
        get_data = acceptance_utility_pool.get_report_data(data,state_condition)
        report_utility_pool = self.env['report.utility']
        op_unit_obj = self.env.user.default_operating_unit_id
        data['address'] = report_utility_pool.getAddressByUnit(op_unit_obj)

        docargs = {
            'doc_ids': self._ids,
            'docs': self,
            'record': data,
            'lines': get_data['acceptances'],
            'address': data['address'],
            'total': get_data['total'],

        }
        return self.env['report'].render('lc_sales_local_report.local_second_acceptance_temp', docargs)

class AcceptanceReportsUtility(models.TransientModel):
    _name = 'acceptance.report.utility'

    def get_report_data(self, data,state_condition):
        acceptances = []
        current_date =  fields.Date.context_today(self)

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
                              ps.to_sales_date as dispatch_to_sale,
                              ps.to_buyer_date as dispatch_to_customer,
                              ps.to_buyer_bank_date as buyer_bank_date,
                              ps.to_seller_bank_date as seller_bank_date,
                              ps.comment as comment,
                              rc.symbol as currency,
                              (CASE
                                  WHEN ps.to_buyer_bank_date is not null THEN date('%s') - date(ps.to_buyer_bank_date)
                                  WHEN ps.to_seller_bank_date is not null THEN date('%s') - date(ps.to_seller_bank_date)
                                  WHEN ps.to_buyer_date is not null THEN date('%s') - date(ps.to_buyer_date)
                                  WHEN ps.to_sales_date is not null THEN date('%s') - date(ps.to_sales_date)
                                ELSE 0
                              END) as aging
                       FROM product_template pt
                          JOIN product_product pp on pp.product_tmpl_id = pt.id
                          JOIN shipment_product_line sp on pp.id = sp.product_id
                          JOIN purchase_shipment ps on ps.id = sp.shipment_id
                          JOIN letter_credit lc on lc.id = ps.lc_id
                          LEFT JOIN res_partner rp on lc.second_party_applicant = rp.id
                          LEFT JOIN res_bank rb on lc.first_party_bank = rb.id
                          LEFT JOIN res_currency rc on lc.currency_id = rc.id
                       WHERE pt.id = %s AND lc.type = 'export' AND lc.region_type = 'local' AND ps.state in %s
                       ORDER BY pt.id ASC
                    '''% (current_date,current_date,current_date,current_date,product_temp_id,state_condition)

        self.env.cr.execute(sql_in_tk)
        for vals in self.env.cr.dictfetchall():
            if vals:
                sale_person_list = []
                lc_objs = self.env['letter.credit'].search([('id','=',vals['lc_id'])])
                for pi_id in lc_objs.pi_ids_temp:
                    for so_id in pi_id.so_ids:
                        sale_person_list.append(so_id.user_id.name)
                sale_persons = ','.join(sale_person_list)
                vals.update({'sale_persons': sale_persons,})

                total_value['total_val'] = total_value['total_val'] + vals['value']
                vals['value'] = formatLang(self.env, vals['value']) if vals['value'] else None
                acceptances.append(vals)

        total_value['total_val'] = formatLang(self.env, total_value['total_val']) if total_value['total_val'] else None
        return {'acceptances': acceptances,'total': total_value}
