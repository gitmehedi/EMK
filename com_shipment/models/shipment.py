from odoo import api, fields, models, _

from openerp.addons.commercial.models.utility import Status, UtilityNumber



class Shipment(models.Model):

    _name = 'purchase.shipment'
    _description = 'Shipment'
    _inherit = ['mail.thread']
    _order = "id desc"

    name = fields.Char(string='Number', required=True, index=True, default=lambda self: self.env.context.get('shipment_number'))
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

    lc_id = fields.Many2one("letter.credit", string='LC Number', ondelete='cascade', default=lambda self: self.env.context.get('lc_id'))
    # bill_of_landin_id = fields.Many2one('bill.of.landing', string='Bill of Landing',ondelete="cascade")
    # packing_list_id = fields.Many2one('packing.list', string='Packing List', ondelete="cascade")




class LetterOfCredit(models.Model):

    _inherit = 'letter.credit'

    shipment_ids = fields.One2many('purchase.shipment', 'lc_id', string='Shipments')

    @api.multi
    def action_shipment(self):

        self.write({'state': 'progress'})
        res = self.env.ref('com_shipment.view_shipment_form')
        if not self.shipment_ids:
            shipmentNo = 1
        else:
            shipmentNo = len(self.shipment_ids) + 1

        comm_utility_pool = self.env['commercial.utility']
        note = comm_utility_pool.getStrNumber(shipmentNo) + ' ' + Status.AMENDMENT.value

        result = {'name': _('Shipment'),
                  'view_type': 'form',
                  'view_mode': 'form',
                  'view_id': res and res.id or False,
                  'res_model': 'purchase.shipment',
                  'context': {'shipment_number': comm_utility_pool.getStrNumber(shipmentNo) +' Shipment','lc_id': self.id},
                  'type': 'ir.actions.act_window',
                  'target': 'current'}

        return result
