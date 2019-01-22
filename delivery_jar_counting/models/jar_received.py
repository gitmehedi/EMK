from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError, Warning
import datetime


class JarReceived(models.Model):
    _name = 'jar.received'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'JAR Received'
    _rec_name = 'partner_id'
    _order = 'id DESC'

    partner_id = fields.Many2one('res.partner', string='Customer', domain=[('customer', '=', True)], required=True,
                                 track_visibility='onchange', )
    due_jar = fields.Integer(string='Due Jar till today', readonly=False, track_visibility='onchange')
    jar_received = fields.Integer(string='# Jar Received', )

    packing_mode = fields.Many2one('product.packaging.mode', string='Jar Type',
                                   domain=[('is_jar_bill_included', '=', False)])

    jar_type = fields.Char(string='Jar Type')
    date = fields.Date(string='Date')




    state = fields.Selection([
        ('draft', "Draft"),
        ('confirmed', "Confirmed"),
    ], default='draft', track_visibility='onchange')

    @api.model
    def create(self, vals):

        pack_mode = self.env['product.packaging.mode'].search([('id','=',vals['packing_mode'])])
        if pack_mode.uom_id:
            vals['jar_type'] = (pack_mode.uom_id.name).upper().strip()
        else:
            vals['jar_type'] = pack_mode.display_name.upper().strip()

        vals['date'] = datetime.datetime.now().date()

        return super(JarReceived, self).create(vals)


    @api.multi
    def write(self, vals):
        pack_mode = self.env['product.packaging.mode'].search([('id', '=', self.packing_mode.id)])
        if pack_mode.uom_id:
            vals['jar_type'] = (pack_mode.uom_id.name).upper().strip()
        else:
            vals['jar_type'] = pack_mode.display_name.upper().strip()

        return super(JarReceived, self).write(vals)



    @api.onchange('packing_mode')
    def _onchange_packing_mode(self):
        if self.partner_id:

            jar_rcv_obj = self.env['jar.received'].search(
                [('state', '=', 'confirmed'), ('packing_mode', '=', self.packing_mode.id),
                 ('partner_id', '=', self.partner_id.id)], order='id DESC',
                limit=1)

            if jar_rcv_obj:
                self.due_jar = jar_rcv_obj.due_jar - jar_rcv_obj.jar_received
            else:
                delivery_jar_count_obj = self.env['delivery.jar.count'].search(
                    [('packing_mode_id', '=', self.packing_mode.id), ('partner_id', '=', self.partner_id.id)])

                total_jar_count = 0
                for deli_jar in delivery_jar_count_obj:
                    total_jar_count += deli_jar.jar_count

                #self.challan_id = delivery_jar_count_obj.challan_id


                self.due_jar = total_jar_count


    def action_confirm(self):
        self.state = 'confirmed'



    # @api.multi
    # def unlink(self):
    #     for jars in self:
    #         if jars.state != 'draft':
    #             raise UserError('You can not delete record which is in Confirmed state')
    #         jars.unlink()
    #     return super(JarReceived, self).unlink()
