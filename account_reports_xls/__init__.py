# -*- coding: utf-8 -*-
have_report_xlsx = False
try:
    from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
    have_report_xlsx = True
except ImportError:
    import logging
    logging.getLogger(__name__).warn('Module report_xlsx is not available')

if have_report_xlsx:
    from . import report
