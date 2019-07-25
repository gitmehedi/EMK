from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class RFQEmailTemplateWizard(models.TransientModel):
    _name = 'rfq.email.template.wizard'

    @api.model
    def _default_body_text(self):
        template = self.env.ref('gbs_purchase_rfq.purchase_rfq_email_template')
        return template.body_html

    subject = fields.Char('Subject', required= True)
    supplier_ids = fields.Many2many('res.partner', string='Supplier', required=True,domain=[('supplier', '=', True),('parent_id', '=', False)])
    massage = fields.Text('Notes', required=True,default=_default_body_text)
    # relational field
    product_lines = fields.One2many('rfq.email.template.line.wizard', 'rfq_temp_id', string='Product(s)')

    @api.multi
    def send_mail(self):
        # data load from previous wizard
        if self.env.context.get('vals'):
            vals = []
            for obj in self.env.context.get('vals'):
                vals.append((0, 0, {'product_id': obj['product_id'],
                                    'product_qty': obj['product_qty'],
                                    'product_uom_id': obj['product_uom_id']
                                    }))
            self.product_lines = vals
        else:
            self.product_lines = []

        # mail sender
        email_server_obj = self.env['ir.mail_server'].search([], order='id ASC', limit=1)
        template = self.env.ref('gbs_purchase_rfq.purchase_rfq_email_template')
        template.write({
            'subject': self.subject,
            'email_from': email_server_obj.name,
            'body_html': self.massage,
        })

        if self.supplier_ids:
            for i in self.supplier_ids:
                if i.email:
                    template.write({
                        'email_to': i.email})
                    self.env['mail.template'].browse(template.id).send_mail(self.id)
                else:
                    raise UserError(_('Unable to send mail because %s has no email address.')%i.name)





class RFQEmailProductLineWizard(models.TransientModel):
    _name = 'rfq.email.template.line.wizard'

    rfq_temp_id = fields.Many2one('rfq.email.template.wizard', string='RFQ Send', ondelete='cascade')
    product_id = fields.Char(string='Product')
    product_qty = fields.Float(string='Quantity')
    product_uom_id = fields.Char(string='Unit of Measure')