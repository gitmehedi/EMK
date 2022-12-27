import json

from odoo import fields, models, api
from lxml import etree


class InheritedProformaInvoice(models.Model):
    _inherit = 'proforma.invoice'

    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        result = super(InheritedProformaInvoice, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if view_type == 'form' or view_type == 'tree':
            company = self.env.user.company_id
            config = self.env['commission.configuration'].search([('customer_type', 'in', company.customer_types.ids or []), ('functional_unit', 'in', company.branch_ids.ids or [])], limit=1)

            if not config.show_packing_mode:
                doc = etree.XML(result['arch'])
                for field in doc.xpath("//field[@name='pack_type']"):
                    modifiers = json.loads(field.get('modifiers', '{}'))
                    modifiers['invisible'] = True
                    modifiers['tree_invisible'] = True
                    modifiers['column_invisible'] = True
                    field.set('modifiers', json.dumps(modifiers))

                result['arch'] = etree.tostring(doc)

        return result
