from odoo import fields, models, api
from lxml import etree


class InheritedProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(InheritedProductTemplate, self).fields_view_get(view_id=view_id, view_type=view_type,
                                                                    toolbar=toolbar,
                                                                    submenu=submenu)

        doc = etree.XML(res['arch'])
        no_create_edit_button = self.env.context.get('no_create_edit_button')
        if not self.env.user.has_group('gbs_application_group.group_sales_product_manager'):
            if no_create_edit_button:
                if view_type == 'form' or view_type == 'kanban' or view_type == 'tree':
                    for node_form in doc.xpath("//kanban"):
                        node_form.set("create", 'false')
                        node_form.set("edit", 'false')
                    for node_form in doc.xpath("//tree"):
                        node_form.set("create", 'false')
                        node_form.set("edit", 'false')
                    for node_form in doc.xpath("//form"):
                        node_form.set("create", 'false')
                        node_form.set("edit", 'false')
        res['arch'] = etree.tostring(doc)
        return res

    def toggle_active(self):
        if self.active:
            self.message_post(body="Product Template Archived")
        else:
            self.message_post(body="Product Template Activated")
        res = super(InheritedProductTemplate, self).toggle_active()
        return res



