from odoo import api, fields, models


class Shipment(models.Model):

    _name = 'lc.shipment'
    _description = 'Shipment'
    _inherit = ['mail.thread']
    _order = "id desc"

    name = fields.Char(string='Number', required=True, index=True)
    comments = fields.Text(string='Comments')

    etd_date = fields.Date('ETD Date', help="Estimated Time of Departure")

    eta_date = fields.Date('ETD Date', help="Estimated Time of Arrival")
    arrival_date = fields.Date('Arrival Date')

    state = fields.Selection(
        [('draft', "Draft"),
         ('on_board', "Shipment On Board"),
         ('receive_doc', "Receive Document"),
         ('eta', "ETA"),
         ('cnf_quotation', "C&F Quotation"),
         ('approve_cnf_quotation', "Approve C&F Quotation"),
         ('cnf_clear', "C&F Clear"),
         ('gate_in', "Gate In"),
         ('done', "Done")], default='draft')

    lc_id = fields.Many2one("letter.credit", string='LC Number', ondelete='cascade')
    # bill_of_landin_id = fields.Many2one('bill.of.landing', string='Bill of Landing',ondelete="cascade")
    # packing_list_id = fields.Many2one('packing.list', string='Packing List', ondelete="cascade")

class LetterOfCredit(models.Model):

    _inherit = 'letter.credit'

    shipment_ids = fields.One2many('lc.shipment', 'lc_id', string='Shipments')
