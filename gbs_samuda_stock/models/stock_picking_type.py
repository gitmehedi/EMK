# -*- coding: utf-8 -*-
from odoo import api, fields, models

class PickingType(models.Model):
    _inherit = 'stock.picking.type'

    code = fields.Selection([('incoming', 'Vendors'),
                             ('outgoing', 'Customers'),
                             ('internal', 'Internal'),
                             ('outgoing_return', 'Customers Return'),
                             ('incoming_return', 'Vendors Return'),
                             ('loan_outgoing', 'Loan'),
                             ('operating_unit_transfer', 'Operating Unit Transfer')
                             ],
                            'Type of Operation', required=True)