from odoo import api, fields, models, _
from odoo.tools.misc import formatLang


class HrEmpLeaveReport(models.AbstractModel):
    _name = 'report.letter_of_credit_report.template_letter_of_credit_report'

    lc_query = """ SELECT DISTINCT(lc.id), lc.name, lc.lc_value, lc.issue_date, lc.expiry_date, 
                                  lc.shipment_date, lc.discharge_port, partner.name AS party, lc.state
                           FROM letter_credit lc
                           LEFT JOIN purchase_shipment ship ON ship.lc_id = lc.id
                           LEFT JOIN res_partner partner ON partner.id = lc.second_party_beneficiary
                           WHERE lc.type = 'import' AND lc.state != 'amendment'"""

    @api.multi
    def render_html(self, docids, data=None):

        report_type = data['report_type']

        if report_type == 'Active':
            self.lc_query += "AND lc.state NOT IN ('done', 'cancel')"
        elif report_type == 'Done':
            self.lc_query += "AND lc.state = 'done'"
        elif report_type == 'Cancel':
            self.lc_query += "AND lc.state = 'cancel'"

        self._cr.execute(self.lc_query)
        data_list = self._cr.fetchall()
        lc_pool = self.env['letter.credit']

        lc_list = []
        for row in data_list:
            lc_obj = {}
            lc_obj['lc_number'] = row[1]
            lc_obj['amount'] = formatLang(self.env,row[2])
            lc_obj['lc_date'] = row[3]
            lc_obj['exp_date'] = row[4]
            lc_obj['ship_date'] = row[5]
            lc_obj['discharging_port'] = row[6]
            lc_obj['party_name'] = row[7]
            lc_obj['state'] = self.getLCState(row[8])
            lc_obj['initial_price'] = row[2]

            lc = lc_pool.search([('id', '=', int(row[0]))])

            prName = ""
            prDate = ""
            for po in lc.po_ids:
                if po.requisition_id:
                    prName += po.requisition_id.name + " "
                    prDate += po.requisition_id.requisition_date + " "

            lc_obj['pr_no'] = prName
            lc_obj['pr_date'] = prDate

            shipment_list = []
            rowspan = 1
            if lc.shipment_ids:
                rowspan = rowspan + len(lc.shipment_ids)
                for shipment in lc.shipment_ids:
                    sh_obj = {}
                    sh_obj['shipment_number'] = shipment.name
                    sh_obj['etd'] = shipment.etd_date
                    sh_obj['state'] = self.getShipmentStateMsg(shipment.state)

                    product_list = []
                    if shipment.shipment_product_lines:
                        rowspan = rowspan + len(shipment.shipment_product_lines)
                        for product in shipment.shipment_product_lines:
                            p_obj = {}
                            p_obj['product_name'] = product.name
                            p_obj['qty'] = str(product.product_qty) + "   " + product.product_uom.name
                            product_list.append(p_obj)

                    sh_obj['product_list'] = product_list

                    shipment_list.append(sh_obj)

            lc_obj['shipment_list'] = shipment_list
            lc_obj['rowspan'] = rowspan

            lc_list.append(lc_obj)

        docargs = {
            'lists': lc_list,
            'report_type' : data['report_type']
        }

        return self.env['report'].render('letter_of_credit_report.template_letter_of_credit_report', docargs)


    def getLCState(self, state):
        if state == 'draft':
            return "Draft"
        elif state == 'open':
            return "Open the LC"
        elif state == 'confirmed':
            return "Confirmed"
        elif state == 'progress':
            return "In Progress"
        elif state == 'done':
            return "Done"
        elif state == 'cancel':
            return "Cancel"
    def getShipmentStateMsg(self,state):
        if state == 'draft':
            return "Shipment in Draft"
        elif state == 'on_board':
            return "Shipment On Board"
        elif state == 'receive_doc':
            return "Receive Doc from Supplier"
        elif state == 'send_to_cnf':
            return "Document Send TO C&F"
        elif state == 'eta':
            return "ETA"
        elif state == 'cnf_quotation':
            return "Collect C&F Quotation"
        elif state == 'approve_cnf_quotation':
            return "Approve C&F Quotation"
        elif state == 'cnf_clear':
            return "C&F Clear the Shipment"
        elif state == 'gate_in':
            return "Product Gate In"
        elif state == 'Shipment Done':
            return "Done"
        elif state == 'cancel':
            return "Cancel the Shipment"