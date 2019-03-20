# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class SupplierCategory(models.Model):
    _name = 'supplier.category'

    name = fields.Char('Name', required=True, size=40,
                       help="Name used to identify category of the supplier")


