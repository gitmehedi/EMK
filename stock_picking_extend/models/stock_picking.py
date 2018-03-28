# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Picking(models.Model):
    _inherit = "stock.picking"

    receive_type = fields.Selection([
        ('loan', 'Loan'),
        ('other', 'Other')],
        readonly=True,states={'draft': [('readonly', False)]})

    # gate_pass = fields.Char(
    #     'Gate Pass', index=True,
    #     states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
    #     help="Reference of the Gate Pass")
    # qc_need = fields.Boolean(
    #     'QC Need',default=False,help="Decision field that QC need or not")
    # check_do_new_transfer = fields.Boolean(
    #     'Check', default=False, compute="_compute_do_new_transfer")
    # check_qc_need = fields.Boolean(
    #     'Check', default=False, compute="_compute_qc_need")
    # state = fields.Selection([
    #     ('draft', 'Draft'), ('cancel', 'Cancelled'),
    #     ('waiting', 'Waiting Another Operation'),
    #     ('confirmed', 'Waiting Availability'),
    #     ('partially_available', 'Partially Available'),
    #     ('assigned', 'Available'),
    #     ('quality_control', 'Quality Control'),
    #     ('done', 'Done')],
    #     string='Status', compute='_compute_state',
    #     copy=False, index=True, readonly=True, store=True, track_visibility='onchange',
    #     help=" * Draft: not confirmed yet and will not be scheduled until confirmed\n"
    #          " * Waiting Another Operation: waiting for another move to proceed before it becomes automatically available (e.g. in Make-To-Order flows)\n"
    #          " * Waiting Availability: still waiting for the availability of products\n"
    #          " * Partially Available: some products are available and reserved\n"
    #          " * Ready to Transfer: products reserved, simply waiting for confirmation.\n"
    #          " * Transferred: has been processed, can't be modified or cancelled anymore\n"
    #          " * Quality Control: If product is qc passed then transfer done otherwise transfer stoped and product can be return\n"
    #          " * Cancelled: has been cancelled, can't be confirmed anymore")
    #
    # @api.multi
    # @api.depends('qc_need')
    # def _compute_do_new_transfer(self):
    #     for rec in self:
    #         if rec.qc_need == False:
    #             if rec.state in ['draft','partially_available','assigned']:
    #                 rec.check_do_new_transfer = True
    #         if rec.state == 'quality_control':
    #             rec.check_do_new_transfer = True
    #
    # @api.multi
    # @api.depends('qc_need')
    # def _compute_qc_need(self):
    #     for rec in self:
    #         if rec.qc_need == True:
    #             if rec.state in ['assigned']:
    #                 rec.check_qc_need = True
    #
    # @api.one
    # def button_qc(self):
    #     self.state = 'quality_control'

