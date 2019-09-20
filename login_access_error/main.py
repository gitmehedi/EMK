from odoo import http, _
from odoo.http import request
from odoo.addons.website.controllers.main import Website


class ExtendWebsite(Website):

    @http.route(website=True, auth="public")
    def web_login(self, redirect=None, *args, **kw):
        response = super(Website, self).web_login(redirect=redirect, *args, **kw)
        if not redirect and 'login_success' in request.params:
            if request.env['res.users'].browse(request.uid).has_group('base.group_user'):
                redirect = '/web?' + request.httprequest.query_string
            else:
                return request.render('web.login')
            return http.redirect_with_hash(redirect)
        return response
