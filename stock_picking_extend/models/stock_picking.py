# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Picking(models.Model):
    _inherit = "stock.picking"

    transfer_type = fields.Selection([
        ('inventory', 'Inventory'),
        ('sale', 'Sale')],
        readonly=True)
    gate_pass = fields.Char(
        'Gate Pass', index=True,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        help="Reference of the Gate Pass")
    state = fields.Selection([
        ('draft', 'Draft'), ('cancel', 'Cancelled'),
        ('waiting', 'Waiting Another Operation'),
        ('confirmed', 'Waiting Availability'),
        ('partially_available', 'Partially Available'),
        ('assigned', 'Available'),
        ('quality_control', 'Quality Control'),
        ('done', 'Done')],
        string='Status', compute='_compute_state',
        copy=False, index=True, readonly=True, store=True, track_visibility='onchange',
        help=" * Draft: not confirmed yet and will not be scheduled until confirmed\n"
             " * Waiting Another Operation: waiting for another move to proceed before it becomes automatically available (e.g. in Make-To-Order flows)\n"
             " * Waiting Availability: still waiting for the availability of products\n"
             " * Partially Available: some products are available and reserved\n"
             " * Ready to Transfer: products reserved, simply waiting for confirmation.\n"
             " * Transferred: has been processed, can't be modified or cancelled anymore\n"
             " * Quality Control: If product is qc passed then transfer done otherwise transfer stoped and product can be return\n"
             " * Cancelled: has been cancelled, can't be confirmed anymore")