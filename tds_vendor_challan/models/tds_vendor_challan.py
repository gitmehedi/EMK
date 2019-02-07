from odoo import models, fields, api, _
from odoo.exceptions import UserError


class TdsVendorChallan(models.Model):
    _name = 'tds.vendor.challan'
    _inherit = ['mail.thread']
    _order = 'date desc'
    _rec_name = 'supplier_id'
    _description = 'TDS Vendor Challan'

    supplier_id = fields.Many2one('res.partner', string="Supplier", track_visibility='onchange')
    operating_unit_id = fields.Many2one('operating.unit', string='Branch', track_visibility='onchange')
    date = fields.Date(string='Date', track_visibility='onchange', help="Creation date.")
    deposit_date = fields.Datetime(string='Deposit Date', readonly=True, track_visibility='onchange')
    deposit_approver = fields.Many2one('res.users', string='Deposit By', readonly=True,
                                       help="who is deposited.", track_visibility='onchange')
    distribute_date = fields.Datetime(string='Distribute Date', readonly=True, track_visibility='onchange')
    distribute_approver = fields.Many2one('res.users', string='Distribute By', readonly=True,
                                          help="who is distributed.", track_visibility='onchange')
    line_ids = fields.One2many('tds.vendor.challan.line', 'parent_id', string='Vendor Challan', select=True,
                               track_visibility='onchange')
    total_amount = fields.Float(string='Total', readonly=True, track_visibility='onchange', compute='_compute_amount')

    state = fields.Selection([
        ('draft', "Pending"),
        ('deposited', "Deposited"),
        ('distributed', "Distributed"),
        ('cancel', "Cancel"),
    ], default='draft', track_visibility='onchange')

    ####################################################
    # Business methods
    ####################################################

    @api.multi
    @api.depends('line_ids')
    def _compute_amount(self):
        for rec in self:
            rec.total_amount = sum([line.total_bill for line in rec.line_ids])

    @api.multi
    def action_deposited(self):
        for record in self:
            if record.state not in ('draft'):
                raise UserError(
                    _("Selected record cannot be deposited as they are not in 'Pending' state."))
            for line in record.line_ids:
                line.write({'state': 'deposited', 'challan_provided': line.undistributed_bill})
            res = {
                'state': 'deposited',
                'deposit_approver': record.env.user.id,
                'deposit_date': fields.Datetime.now(),
            }
            record.write(res)

    @api.multi
    def action_distributed(self):
        for record in self:
            if record.state not in ('deposited'):
                raise UserError(
                    _("Selected record cannot be distributed as they are not in 'Deposited' state."))
            for line in record.line_ids:
                line.write({'state': 'distributed', 'undistributed_bill': 0.0})
            res = {
                'state': 'distributed',
                'distribute_approver': record.env.user.id,
                'distribute_date': fields.Datetime.now(),
            }
            record.write(res)

    @api.one
    def action_cancel(self):
        for line in self.line_ids:
            line.acc_move_line_id.write({'is_deposit': False})
            line.write({'state': 'cancel'})
        res = {
            'state': 'cancel',
        }
        self.write(res)

    ####################################################
    # ORM Overrides methods
    ####################################################

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_('You cannot delete a record which is not draft state!'))
        return super(TdsVendorChallan, self).unlink()


class TdsVendorChallanLine(models.Model):
    _name = 'tds.vendor.challan.line'

    supplier_id = fields.Many2one('res.partner', string="Supplier")
    challan_provided = fields.Float(String='Challan Provided')
    total_bill = fields.Float(String='Total Bill')
    undistributed_bill = fields.Float(String='Undistributed Bill')
    parent_id = fields.Many2one('tds.vendor.challan')
    acc_move_line_id = fields.Many2one('account.move.line')
    operating_unit_id = fields.Many2one('operating.unit', string='Branch', track_visibility='onchange')

    state = fields.Selection([
        ('draft', "Draft"),
        ('deposited', "Deposited"),
        ('distributed', "Distributed"),
        ('cancel', "Cancel"),
    ], default='draft', track_visibility='onchange')
