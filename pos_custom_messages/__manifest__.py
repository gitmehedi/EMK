# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
#################################################################################
{
	'name' : 'POS Custom Messages',
	'summary' : 'Used to show messages and warnings in POS',
	'version' : '1.0',
	'category': 'Point Of Sale',
	"sequence": 1,
	"depends" : ['point_of_sale'],
	'description': """

**Help and Support**
================
.. |icon_features| image:: pos_custom_messages/static/description/icon-features.png
.. |icon_support| image:: pos_custom_messages/static/description/icon-support.png
.. |icon_help| image:: pos_custom_messages/static/description/icon-help.png

|icon_help| `Help <http://webkul.uvdesk.com/en/customer/create-ticket/>`_ |icon_support| `Support <http://webkul.uvdesk.com/en/customer/create-ticket/>`_ |icon_features| `Request new Feature(s) <http://webkul.uvdesk.com/en/customer/create-ticket/>`_
	""",
	'author': 'Webkul Software Pvt. Ltd.',
	'website': 'http://www.webkul.com',
	'data':	['views/template.xml'],
	'qweb': ['static/src/xml/pos_custom_messages.xml'],
	"installable": True,
	"application": True,
	"auto_install": False,
	'images': ['static/description/Banner.png'],
'pre_init_hook': 'pre_init_check',
'live_test_url':'http://odoodemo.webkul.com/?module=pos_custom_messages&version=10.0',
}
