from odoo import _, api, fields, models
from lxml import etree
from odoo.exceptions import UserError, ValidationError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(AccountInvoice, self).fields_view_get(view_id=view_id, view_type=view_type,
                                                          toolbar=toolbar,
                                                          submenu=submenu)

        doc = etree.XML(res['arch'])
        no_create_edit_button = self.env.context.get('no_create_edit_button')
        if no_create_edit_button:
            if view_type == 'form' or view_type == 'kanban' or view_type == 'tree':
                for node_form in doc.xpath("//kanban"):
                    node_form.set("create", 'false')
                for node_form in doc.xpath("//tree"):
                    node_form.set("create", 'false')
                for node_form in doc.xpath("//form"):
                    node_form.set("create", 'false')

        res['arch'] = etree.tostring(doc)
        return res

    @api.model
    def _default_manual_invoice(self):
        if self._context.get('create_edit_button'):
            return True
        else:
            return False

    manual_invoice = fields.Boolean(default=lambda self: self._default_manual_invoice(), store=True)