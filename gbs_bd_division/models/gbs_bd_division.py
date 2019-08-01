from odoo import models, fields, api,_


class BDDivision(models.Model):
    _name = 'bd.division'

    name = fields.Char(string='Division',required=True)


class BDDistrict(models.Model):
    _name = 'bd.district'

    name = fields.Char(string='District',required=True)
    division_id = fields.Many2one('bd.division', string='Division')


class BDUpazila(models.Model):
    _name = 'bd.upazila'

    name = fields.Char(string='Upazila',required=True)
    division_id = fields.Many2one('bd.division', string='Division')
    district_id = fields.Many2one('bd.district', string='District')


class BDPostalCode(models.Model):
    _name = 'bd.postal.code'

    name = fields.Char(string='Postal Code',required=True)
    upazila_id = fields.Many2one('bd.upazila', string='Upazila')