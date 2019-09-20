from odoo import api, fields, models,_
from odoo.exceptions import UserError, ValidationError
from openerp.addons.commercial.models.utility import Status, UtilityNumber

class LetterOfCredit(models.Model):
    _name = 'letter.credit'
    _description = 'Letter of Credit (L/C)'
    _inherit = ['mail.thread']
    _order = "issue_date desc"

    # Import -> Applicant(Samuda)

    name = fields.Char(string='LC Number', index=True,readonly=True)
    title = fields.Text(string='Description')

    type = fields.Selection([
        ('export', 'Export'),
        ('import', 'Import'),
    ], string="LC Type",
        help="Export: Product Export.\n"
             "Import: Product Import.", default="import")

    region_type = fields.Selection([
        ('local', 'Local'),
        ('foreign', 'Foreign'),
    ], string="Region Type",readonly=True,
        help="Local: Local LC.\n"
             "Foreign: Foreign LC.")

    first_party = fields.Many2one('res.company', string='Candidate', required=True)
    # first_party_bank = fields.Many2one('res.bank', string='Bank')
    first_party_bank_acc = fields.Many2one('res.partner.bank', string='Bank Account', domain=[('is_company_account', '=', True)], required=True)

    second_party_applicant = fields.Many2one('res.partner', string='Applicant', domain = "[('customer', '=', True)]")
    second_party_beneficiary = fields.Many2one('res.partner', string='Candidate', domain="[('supplier', '=', True)]")

    second_party_bank = fields.Text(string='Bank', required=False)

    require_lien = fields.Boolean(string='Require Lien', default=False)
    lien_bank = fields.Text(string='LC Lien Bank')
    lien_date = fields.Date('LC Lien Date')

    lc_value = fields.Float(string='LC Value', readonly=False, states={'approved': [('readonly', True)]}, track_visibility='onchange', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', track_visibility='onchange')

    insurance_company_name = fields.Char(string='Insurance Company Name')
    insurance_number = fields.Char(string='Insurance Number')
    insurance_bill = fields.Float(string='Insurance Bill')

    landing_port = fields.Char(string='Landing Port', track_visibility='onchange')
    discharge_port = fields.Char(string='Discharge Port', track_visibility='onchange')
    cnf_agent = fields.Char(string='C&F Agent', track_visibility='onchange')

    issue_date = fields.Date('Issue Date', track_visibility='onchange')
    expiry_date = fields.Date('Expiry Date', track_visibility='onchange')
    shipment_date = fields.Date('Shipment Date', track_visibility='onchange')

    amendment_date = fields.Date('Amendment Date', track_visibility='onchange')

    master_lc_number = fields.Char(string='Master LC Number', track_visibility='onchange')
    hs_code = fields.Char(string='HS Code', track_visibility='onchange')
    tolerance = fields.Float(string='Tolerance (%)', track_visibility='onchange')## 10% plus and minus value
    payment_terms = fields.Char(string='Payment Terms', track_visibility='onchange')
    period_of_presentation = fields.Float(string='Period of Presentation', track_visibility='onchange')
    ship_mode = fields.Char(string='Ship Mode', track_visibility='onchange')
    inco_terms = fields.Many2one('stock.incoterms',string='Incoterms', track_visibility='onchange')
    partial_shipment = fields.Boolean(string='Allow Partial Shipment', track_visibility='onchange')
    trans_shipment =  fields.Boolean(string='Allow Trans. Shipment', track_visibility='onchange')
    lc_mode = fields.Char(string='LC Mode', track_visibility='onchange')
    terms_condition = fields.Text(string='Terms of Condition')
    remarks = fields.Text(string='Remarks')

    # attachment_ids = fields.One2many('ir.attachment', 'res_id', string='Attachments')
    attachment_ids = fields.One2many('ir.attachment', 'res_id', string='Attachments',domain=[('res_model', '=', 'letter.credit')])

    # For LC Revision

    current_revision_id = fields.Many2one('letter.credit', 'Current revision', readonly=True, copy=True,
                                          ondelete='cascade')
    old_revision_ids = fields.One2many('letter.credit', 'current_revision_id', 'Old revisions', readonly=True,
                                       context={'active_test': False})
    revision_number = fields.Integer('Revision', copy=False)
    unrevisioned_name = fields.Char('LC Reference', copy=True, readonly=True)
    active = fields.Boolean('Active', default=True, copy=True)
    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit', required=True)

    state = fields.Selection([
        ('draft', "Draft"),
        ('open', "Open"),
        ('confirmed', "Confirmed"),
        ('amendment', "Amendment"),
        ('progress', "In Progress"),
        ('done', "Done"),
        ('cancel', "Cancel")
    ], default='draft')

    last_note = fields.Char(string='Step', track_visibility='onchange')

    @api.multi
    @api.onchange('first_party')
    def onchange_company_id(self):
        if self.first_party:
            # self.operating_unit_id = []
            return {'domain': {'operating_unit_id': [('company_id', '=', self.first_party.id)]}}

    # @api.multi
    # @api.constrains('operating_unit_id')
    # def _check_operating_unit_id(self):
    #     for po in self.po_ids:
    #         if self.operating_unit_id.id != po.operating_unit_id.id:
    #             raise ValidationError(_("Operating unit of %s is not same with operating unit of letter of credit.\n"
    #                   "Your purchase order's operating unit and letter of credit's operating unit must be same.") % (po.name))

    @api.multi
    @api.constrains('issue_date')
    def check_date(self):
        if self.issue_date and self.shipment_date:
            if self.issue_date >= self.shipment_date:
                raise ValidationError(_("Shipment Date must be grater than Issue Date !!"))
        elif self.issue_date and self.expiry_date:
            if self.issue_date >= self.expiry_date:
                raise ValidationError(_("Expiry Date must be greater than Issue Date !!"))


    @api.multi
    @api.constrains('shipment_date')
    def check_shipment_date(self):
        if self.shipment_date and self.expiry_date:
            if self.shipment_date >= self.expiry_date:
                raise ValidationError(_("Expiry Date must be greater than Shipment Date !!"))


    @api.multi
    def action_cancel(self):
        for shipment in self.shipment_ids:
            if shipment.state != 'done' and shipment.state != 'cancel':
                raise ValidationError(_("This LC has " + str(len(self.shipment_ids)) +
                                        " shipment(s).Before Cancel this LC, need to Cancel or Done all Shipment(s)."))
        self.state = "cancel"
        self.last_note = "LC Cancel"


    @api.multi
    def unlink(self):
        for lc in self:
            if str(lc.state) != 'draft' and str(lc.state) != 'open':
                raise UserError('You can not delete this.')
            else:
                query = """ delete from ir_attachment where res_id=%s"""
                for att in self.attachment_ids:
                    self._cr.execute(query, tuple([att.res_id]))
                return super(LetterOfCredit, self).unlink()

    @api.constrains('tolerance')
    def _check_qty(self):
        if self.tolerance > 10 :
            raise Warning('You should set "Tolerance" upto 10 !')

    @api.multi
    def action_open(self):
        self.write({'state': 'open','last_note': "LC Open"})
        if self.tolerance > 10 :
            raise Warning('You should set "Tolerance" upto 10 !')

    @api.multi
    def action_confirm(self):
        res = self.env.ref('letter_of_credit.lc_number_wizard')
        result = {
            'name': _('Please Give The Number Of LC'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'lc.number.wizard',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
        }
        return result

    @api.multi
    def action_draft(self):
        self.write({'state': 'draft'})

    @api.one
    @api.constrains('name')
    def _check_name(self):
        if len(self.name) == 0:
            return True

        domain = ['&','&','&',('name', '=', self.name),
                  ('type','=',self.type),
                  ('state', '!=', 'cancel'),
                  ('id', '!=', self.id)]
        if self.search_count(domain):
            raise UserError('LC Number must be unique. You can\'t create duplicate Number')
        return True

    @api.model
    def create(self, vals):
        if 'unrevisioned_name' not in vals:
            if vals.get('name', 'New') == 'New':
                seq = self.env['ir.sequence']
                vals['name'] = seq.next_by_code('letter.credit') or ''
            vals['unrevisioned_name'] = vals['name']
        return super(LetterOfCredit, self).create(vals)

    @api.multi
    def action_revision(self):
        self.ensure_one()
        view_ref = self.env['ir.model.data'].get_object_reference('letter_of_credit', 'view_local_credit_form')
        view_id = view_ref and view_ref[1] or False,
        self.with_context(new_lc_revision=True).copy()

        number = len(self.old_revision_ids)

        comm_utility_pool = self.env['commercial.utility']
        note = comm_utility_pool.getStrNumber(number) + ' ' + "Amendment"

        self.write({'state': self.state, 'last_note': note})
        return {
            'type': 'ir.actions.act_window',
            'name': _('LC'),
            'res_model': 'letter.credit',
            'res_id': self.id,
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'current',
            'nodestroy': True,
            'flags': {'initial_mode': 'edit'},
        }

    @api.returns('self', lambda value: value.id)
    @api.multi
    def copy(self, defaults=None):
        if not defaults:
            defaults = {}
        if self.env.context.get('new_lc_revision'):
            prev_name = self.name
            revno = self.revision_number
            self.write({'revision_number': revno + 1, 'name': '%s-%02d' % (self.unrevisioned_name, revno + 1)})
            if self.env.context.get('amendment_date'):
                defaults.update({'name': prev_name, 'revision_number': revno, 'active': False, 'state': 'amendment',
                                 'current_revision_id': self.id, 'unrevisioned_name': self.unrevisioned_name,
                                 'amendment_date': self.env.context.get('amendment_date') })
            else:
                defaults.update({'name': prev_name, 'revision_number': revno, 'active': False, 'state': 'amendment',
                                 'current_revision_id': self.id, 'unrevisioned_name': self.unrevisioned_name, })
        return super(LetterOfCredit, self).copy(defaults)
