from odoo import api, fields, models, _

from openerp.addons.commercial.models.utility import Status, UtilityNumber

class Shipment(models.Model):

    _name = 'purchase.shipment'
    _description = 'Shipment'
    _inherit = ['mail.thread']
    _order = "id desc"

    name = fields.Char(string='Number', required=True, readonly=True, index=True, default=lambda self: self.env.context.get('shipment_number'))
    comments = fields.Text(string='Comments')

    etd_date = fields.Date('ETD Date', help="Estimated Time of Departure")
    eta_date = fields.Date('ETA Date', help="Estimated Time of Arrival")
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
    shipment_attachment_ids = fields.One2many('ir.attachment', 'res_id', string='Shipment Attachments')

    # Bill Of Lading
    bill_of_lading_number = fields.Char(string='BoL Number', required=True, index=True, help="Bill Of Lading Number")
    shipment_date = fields.Date('Ship on Board', required=True)

    # Packing List
    gross_weight = fields.Float('Gross Weight', required=True)
    net_weight = fields.Float('Net Weight', required=True)

    @api.model
    def create(self, vals):

        self.env['letter.credit'].search([('id', '=', self.env.context.get('lc_id'))], limit=1).write(
            {'last_note': "Initiate " + self.env.context.get('shipment_number')})

        return super(Shipment, self).create(vals)

    @api.multi
    def action_view_shipment(self):

        res = self.env.ref('com_shipment.view_shipment_form')

        result = {'name': _('Shipment'),
                  'view_type': 'form',
                  'view_mode': 'form',
                  'view_id': res and res.id or False,
                  'res_model': 'purchase.shipment',
                  'type': 'ir.actions.act_window',
                  'target': 'current',
                  'res_id': self.id}

        return result

    @api.multi
    def action_edit_shipment(self):

        res = self.env.ref('com_shipment.view_shipment_form')

        result = {'name': _('Shipment'),
                  'view_type': 'form',
                  'view_mode': 'form',
                  'view_id': res and res.id or False,
                  'res_model': 'purchase.shipment',
                  'type': 'ir.actions.act_window',
                  'target': 'current',
                  'res_id': self.id,
                  'flags': {'initial_mode': 'edit'}}

        return result


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
