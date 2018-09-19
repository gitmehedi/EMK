# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class MemberOccupation(models.Model):
    _name = 'member.occupation'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Members Occupation"
    _order = 'id ASC'

    name = fields.Char(string='Title', required=True, size=50, track_visibility='onchange')
    status = fields.Boolean(string='Status', default=True, track_visibility='onchange')

    @api.constrains('name')
    def _check_name(self):
        name = self.search([('name', '=ilike', self.name)])
        if len(name) > 1:
            raise Exception(_('Name should not be duplicate.'))


class MemberSubjectOfInterest(models.Model):
    _name = 'member.subject.interest'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Members Subject of Interest"
    _order = 'id ASC'

    name = fields.Char(string='Title', required=True, size=50, track_visibility='onchange')
    status = fields.Boolean(string='Status', default=True, track_visibility='onchange')

    @api.constrains('name')
    def _check_name(self):
        name = self.search([('name', '=ilike', self.name)])
        if len(name) > 1:
            raise Exception(_('Name should not be duplicate.'))


class MemberCertification(models.Model):
    _name = 'member.certification'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Members Certification"
    _order = 'id ASC'

    name = fields.Char(string='Title', required=True, size=50, track_visibility='onchange')
    status = fields.Boolean(string='Status', default=True, track_visibility='onchange')

    @api.constrains('name')
    def _check_name(self):
        name = self.search([('name', '=ilike', self.name)])
        if len(name) > 1:
            raise Exception(_('Name should not be duplicate.'))
