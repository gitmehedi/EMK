from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = ['res.partner', 'mail.thread']

    name = fields.Char(track_visibility='onchange')
    parent_id = fields.Many2one(track_visibility='onchange')
    website = fields.Char(track_visibility='onchange')
    company_type = fields.Selection(track_visibility='onchange')
    category_id = fields.Many2many(track_visibility='onchange')
    function = fields.Char(track_visibility='onchange')
    tax = fields.Char(track_visibility='onchange')
    vat = fields.Char(track_visibility='onchange')
    bin = fields.Char(track_visibility='onchange')
    tin = fields.Char(track_visibility='onchange')
    title = fields.Many2one(track_visibility='onchange')
    lang = fields.Selection(track_visibility='onchange')
    customer = fields.Boolean(track_visibility='onchange')
    supplier = fields.Boolean(track_visibility='onchange')
    active = fields.Boolean(track_visibility='onchange')
    property_account_receivable_id = fields.Many2one(track_visibility='onchange')
    property_account_payable_id = fields.Many2one(track_visibility='onchange')
    email = fields.Char(track_visibility='onchange')
    phone = fields.Char(track_visibility='onchange')
    fax = fields.Char(track_visibility='onchange')
    mobile = fields.Char(track_visibility='onchange')
    street = fields.Char(track_visibility='onchange')
    street2 = fields.Char(track_visibility='onchange')
    zip = fields.Char(track_visibility='onchange')
    city = fields.Char(track_visibility='onchange')
    state_id = fields.Many2one(track_visibility='onchange')
    country_id = fields.Many2one(track_visibility='onchange')
    company_id = fields.Many2one(track_visibility='onchange')


    """ All functions """
    @api.constrains('name')
    def _check_unique_name(self):
        if self.name:
            name = self.env['res.partner'].search([('name', '=ilike', self.name)])
            if self.supplier == True:
                if len(name) > 1:
                    raise ValidationError('[Unique Error] Vendor Name must be unique!')
            elif self.customer == True:
                if len(name) > 1:
                    raise ValidationError('[Unique Error] Customer Name must be unique!')
            else:
                if len(name) > 1:
                    raise ValidationError('[Unique Error] Name must be unique!')
