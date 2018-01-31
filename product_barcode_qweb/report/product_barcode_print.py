# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more summary.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

# from barcode.writer import ImageWriter
# from barcode import generate
from Code128 import Code128
import base64
from StringIO import StringIO

import os
import time
import math
from openerp.osv import osv
from openerp.report import report_sxw
from openerp.tools import config


class product_barcode_print(report_sxw.rml_parse):
    def prepare_attr(self, ids):
        attrs = self.pool.get('product.attribute.value').read(self.cr, self.uid, ids, ['name', 'attribute_id'])

        name = ""
        for attr in attrs:
            if attr['attribute_id'][1] == 'Size':
                name = name + ", " + attr['name'] if len(name) > 0 else  name + attr['name']

        return "({0})".format(name) if len(name) > 0 else name

    def _getLabelRows(self, form):

        product_obj = self.pool.get('product.product')
        data = []
        result = {}
        product_ids = [int(key) for key, val in form['product_ids'].iteritems()]
        if not product_ids:
            return {}

        products_data = product_obj.read(self.cr, self.uid, product_ids,
                                         ['name', 'default_code', 'attribute_value_ids', 'list_price'])
        for product in products_data:
            for product_row in range(int(math.ceil(float(form['product_ids'].get(str(product['id']))) / 5))):
                label_row = []
                for row in [1, 2, 3, 4, 5]:
                    attr = self.prepare_attr(product['attribute_value_ids'])
                    label_data = {
                        'name': product['name'][:26] + attr,
                        'company_name': self.company_name,
                        'default_code': product['default_code'],
                        'price': product['list_price'],
                    }
                    label_row.append(label_data)
                data.append(label_row)

        if data:
            return data
        else:
            return {}

    def get_custom_data_dir(self):
        my_data_directory = os.path.join(config['data_dir'], "custom_filestore", "product_barcode_qweb")

        if not os.path.exists(my_data_directory):
            os.makedirs(my_data_directory)
        return my_data_directory

    def _generateBarcode(self, barcode_string):  # , height, width):
        fp = StringIO()
        # generate('CODE39', barcode_string, writer=ImageWriter(), add_checksum=False, output=fp)
        # barcode_data = base64.b64encode(fp.getvalue())
        # return '<img style="width: 25mm;height: 7mm;" src="data:image/png;base64,%s" />'%(barcode_data)
        # return barcode_data
        my_data_directory = self.get_custom_data_dir()
        Code128().getImage(barcode_string, path=my_data_directory).save(fp, "PNG")
        barcode_data = base64.b64encode(fp.getvalue())
        return barcode_data

    def __init__(self, cr, uid, name, context):
        super(product_barcode_print, self).__init__(cr, uid, name, context=context)

        user_pool = self.pool.get('res.users')
        user = user_pool.browse(cr, uid, [self.uid], context)
        self.company_name = user.company_id.name

        self.total = 0.0
        self.qty = 0.0
        self.total_invoiced = 0.0
        self.discount = 0.0
        self.total_discount = 0.0
        self.localcontext.update({
            'time': time,
            'getLabelRows': self._getLabelRows,
            'generateBarcode': self._generateBarcode,
        })


class report_product_barcode_print(osv.AbstractModel):
    _name = 'report.product_barcode_qweb.report_product_barcode'
    _inherit = 'report.abstract_report'
    _template = 'product_barcode_qweb.report_product_barcode'
    _wrapped_report_class = product_barcode_print

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
