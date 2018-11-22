from odoo import api, fields, models, _

from openerp.addons.commercial.models.utility import Status, UtilityNumber

class Shipment(models.Model):

    _name = 'purchase.shipment'
    _description = 'Shipment'
    _inherit = ['mail.thread']
    _order = "arrival_date asc"

    name = fields.Char(string='Number', required=True, readonly=True, index=True, default=lambda self: self.env.context.get('shipment_number'))
    comments = fields.Text(string='Comments', track_visibility='onchange')
    etd_date = fields.Date('ETD Date', help="Estimated Time of Departure")
    eta_date = fields.Date('ETA Date', help="Estimated Time of Arrival")
    arrival_date = fields.Date('Arrival Date', )
    cnf_received_date = fields.Date('C&F Received Date', readonly=True)
    cnf_id = fields.Many2one('res.partner', "Supplier", readonly=True)
    comment = fields.Text('Comment')
    transport_by = fields.Char('Transport By')
    vehical_no = fields.Char('Vehicle No')

    operating_unit_id = fields.Many2one('operating.unit', default=lambda self: self.env.context.get('operating_unit_id'))
    company_id = fields.Many2one('res.company', default=lambda self: self.env.context.get('company_id'))

    state = fields.Selection(
        [('draft', "Draft"),
         ('on_board', "Shipment On Board"),
         ('receive_doc', "Transfer Doc"),
         ('send_to_cnf', "Send TO C&F"),
         ('eta', "ETA"),
         ('cnf_quotation', "C&F Quotation"),
         ('approve_cnf_quotation', "Approve"),
         ('cnf_clear', "C&F Clear"),
         ('gate_in', "Gate In"),
         ('done', "Done"),
         ('cancel', "Cancel")], default='draft', track_visibility='onchange')

    lc_id = fields.Many2one("letter.credit", string='LC Number', ondelete='cascade',readonly=True,
                            default=lambda self: self.env.context.get('lc_id'))
    shipment_attachment_ids = fields.One2many('ir.attachment', 'res_id', string='Shipment Attachments', domain=[('res_model', '=', 'purchase.shipment')])

    # Bill Of Lading
    bill_of_lading_number = fields.Char(string='BoL Number', index=True, help="Bill Of Lading Number")
    shipment_date = fields.Date('Ship on Board')

    # Packing List
    gross_weight = fields.Float('Gross Weight')
    net_weight = fields.Float('Net Weight')
    weight_uom = fields.Many2one('product.uom', string='Weight Unit')

    count_qty = fields.Float(string='Count')
    count_uom = fields.Many2one('product.uom', string='Unit')

    # Invoice
    invoice_number = fields.Char(string='Invoice Number')
    invoice_value = fields.Float(string='Invoice Value')

    # @api.multi
    def name_get(self):
        result = []
        for record in self:
            name = record.name
            if record.lc_id:
                name = "%s [%s]" % (record.lc_id.name_get()[0][1], name)
            result.append((record.id, name))
        return result

    @api.model
    def create(self, vals):

        self.env['letter.credit'].search([('id', '=', self.env.context.get('lc_id'))], limit=1).write(
            {'last_note': "Initiate " + self.env.context.get('shipment_number')})

        return super(Shipment, self).create(vals)

    @api.multi
    def action_cancel(self):
        res = self.env.ref('com_shipment.cancel_wizard')
        result = {
            'name': _('Do you want to cancel this shipment?'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'cancel.wizard',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
        }
        return result


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

    #For done_wizard
    @api.multi
    def action_done(self):
        res = self.env.ref('com_shipment.done_wizard')
        result = {
            'name': _('Do you want to done this shipment?'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'done.wizard',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
        }
        return result
    # State Change Actions

    @api.multi
    def action_on_board(self):
        res = self.env.ref('com_shipment.on_board_wizard')
        result = {
            'name': _('Please Enter The Shipment On Board Info'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'on.board.wizard',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
        }
        return result

    api.multi
    def action_send_to_cnf(self):
        res = self.env.ref('com_shipment.send_to_cnf_wizard')
        result = {
            'name': _('Please Enter The Information'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'send.to.cnf.wizard',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
        }
        return result

    @api.multi
    def action_doc_receive(self):
        res = self.env.ref('com_shipment.doc_receive_wizard')
        result = {
            'name': _('Please Enter Receive Document After Shipment'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'doc.receive.wizard',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
        }
        return result

    @api.multi
    def action_eta(self):
        res = self.env.ref('com_shipment.eta_wizard')
        result = {
            'name': _('Please Enter The Information'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'eta.wizard',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
        }
        return result

    @api.multi
    def action_cnf_clear(self):
        res = self.env.ref('com_shipment.cnf_clear_wizard')
        result = {
            'name': _('Please Enter The Information'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'cnf.clear.wizard',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
        }
        return result

    @api.multi
    def action_email_temp(self):
        res = self.env.ref('com_shipment.email_template_wizard')
        result = {
            'name':_('New Message'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model':'email.template.wizard',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
        }
        return result

    @api.multi
    def action_draft(self):
        self.write({'state': 'draft'})

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
        note = comm_utility_pool.getStrNumber(shipmentNo) + ' ' + "Amendment"

        result = {'name': _('Shipment'),
                  'view_type': 'form',
                  'view_mode': 'form',
                  'view_id': res and res.id or False,
                  'res_model': 'purchase.shipment',
                  'context': {'shipment_number': comm_utility_pool.getStrNumber(shipmentNo) +' Shipment',
                              'lc_id': self.id,
                              'operating_unit_id': self.operating_unit_id.id,
                              'company_id': self.first_party.id},
                  'type': 'ir.actions.act_window',
                  'target': 'current'}
        self.env['letter.credit'].search([('id', '=', self.id)])
        return result
