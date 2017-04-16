from openerp import models, fields, api, _


class Dashboard(models.Model):
    _name = 'dashboard.design'

    def _get_json_data(self):
        return [{'values':[{'y': 0, 'x': '2 Jan', 'name': '2 January 2017'},
                         {'y': 0, 'x': '3 Jan', 'name': '3 January 2017'},
                         {'y': 0, 'x': '4 Jan', 'name': '4 January 2017'},
                         {'y': 0, 'x': '5 Jan', 'name': '5 January 2017'},
                         {'y': 0, 'x': '6 Jan', 'name': '6 January 2017'},
                         {'y': 0, 'x': '7 Jan', 'name': '7 January 2017'},
                         {'y': 0, 'x': '8 Jan', 'name': '8 January 2017'},
                         {'y': 0, 'x': '9 Jan', 'name': '9 January 2017'},
                         {'y': 0, 'x': '10 Jan', 'name': '10 January 2017'},
                         {'y': 0, 'x': '11 Jan', 'name': '11 January 2017'},
                         {'y': 0, 'x': '12 Jan', 'name': '12 January 2017'},
                         {'y': 0, 'x': '13 Jan', 'name': '13 January 2017'},
                         {'y': 0, 'x': '14 Jan', 'name': '14 January 2017'},
                         {'y': 0, 'x': '15 Jan', 'name': '15 January 2017'},
                         {'y': 0, 'x': '16 Jan', 'name': '16 January 2017'},
                         # {'y': 0, 'x': u'17 Jan', 'name': u'17 January 2017'},
                         # {'y': 0, 'x': u'18 Jan', 'name': u'18 January 2017'},
                         # {'y': 0, 'x': u'19 Jan', 'name': u'19 January 2017'},
                         # {'y': 0, 'x': u'20 Jan', 'name': u'20 January 2017'},
                         # {'y': 0, 'x': u'21 Jan', 'name': u'21 January 2017'},
                         # {'y': 0, 'x': u'22 Jan', 'name': u'22 January 2017'},
                         # {'y': 0, 'x': u'23 Jan', 'name': u'23 January 2017'},
                         # {'y': 0, 'x': u'24 Jan', 'name': u'24 January 2017'},
                         # {'y': 0, 'x': u'25 Jan', 'name': u'25 January 2017'},
                         # {'y': 0, 'x': u'26 Jan', 'name': u'26 January 2017'},
                         # {'y': 0, 'x': u'27 Jan', 'name': u'27 January 2017'},
                         # {'y': 0, 'x': u'28 Jan', 'name': u'28 January 2017'},
                         # {'y': 0, 'x': u'29 Jan', 'name': u'29 January 2017'},
                         # {'y': 0, 'x': u'30 Jan', 'name': u'30 January 2017'},
                         # {'y': 0, 'x': u'31 Jan', 'name': u'31 January 2017'},
                         {'y': 0, 'x': '1 Feb', 'name': '1 February 2017'}
                        ]}]



    name = fields.Char(string="Name")
    no = fields.Integer(string="Number")
    color = fields.Char(string="Color")

    # product_qty = fields.Integer(string="Product Quantity", default=lambda self: self._get_json_data())

