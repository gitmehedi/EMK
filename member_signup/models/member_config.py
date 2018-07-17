# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class MemberOccupation(models.Model):
    _name = 'member.occupation'
    _description = "Members Occupation"

    name = fields.Char(string='Title', required=True, size=50)
    status = fields.Boolean(string='Status', default=True)

    @api.constrains('name')
    def _check_name(self):
        name = self.search([('name', '=ilike', self.name)])
        if len(name) > 1:
            raise Exception(_('Name should not be duplicate.'))


class MemberSubjectOfInterest(models.Model):
    _name = 'member.subject.interest'
    _description = "Members Subject of Interest"

    name = fields.Char(string='Title', required=True, size=50)
    status = fields.Boolean(string='Status', default=True)

    @api.constrains('name')
    def _check_name(self):
        name = self.search([('name', '=ilike', self.name)])
        if len(name) > 1:
            raise Exception(_('Name should not be duplicate.'))


class MemberCertification(models.Model):
    _name = 'member.certification'
    _description = "Members Certification"

    name = fields.Char(string='Title', required=True, size=50)
    status = fields.Boolean(string='Status', default=True)

    @api.constrains('name')
    def _check_name(self):
        name = self.search([('name', '=ilike', self.name)])
        if len(name) > 1:
            raise Exception(_('Name should not be duplicate.'))
