# -*- coding: utf-8 -*-
# © 2013 Nicolas Bessi (Camptocamp SA)
# © 2014 Agile Business Group (<http://www.agilebg.com>)
# © 2015 Grupo ESOC (<http://www.grupoesoc.es>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from odoo import api, fields, models
from .. import exceptions

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    """Adds last name and first name; name becomes a stored function field."""
    _inherit = 'res.partner'

    firstname = fields.Char("First Name", index=True, )
    middlename = fields.Char("Middle Name", index=True)
    lastname = fields.Char("Last Name", index=True)
    name = fields.Char(compute="_compute_name", required=False, store=True)

    @api.model
    def create(self, vals):
        """Add inverted names at creation if unavailable."""
        context = dict(self.env.context)
        name = vals.get("name", context.get("default_name"))

        if name is not None:
            # Calculate the splitted fields
            inverted = self._get_inverse_name(name,
                vals.get("is_company",self.default_get(["is_company"])["is_company"]))

            for key, value in inverted.iteritems():
                if not vals.get(key) or context.get("copy"):
                    vals[key] = value

            if not vals['lastname']:
                vals['lastname'] = vals['middlename']
                vals['middlename'] = False
            # Remove the combined fields
            if "name" in vals:
                del vals["name"]
            if "default_name" in context:
                del context["default_name"]

        return super(ResPartner, self.with_context(context)).create(vals)

    @api.multi
    def copy(self, default=None):
        """Ensure partners are copied right.

        Odoo adds ``(copy)`` to the end of :attr:`~.name`, but that would get
        ignored in :meth:`~.create` because it also copies explicitly firstname
        and lastname fields.
        """
        return super(ResPartner, self.with_context(copy=True)).copy(default)

    @api.model
    def default_get(self, fields_list):
        """Invert name when getting default values."""
        result = super(ResPartner, self).default_get(fields_list)

        if not result.get('name'):
            return result

        inverted = self._get_inverse_name(result["name"],result.get("is_company", False))

        for field in inverted:
            if field in fields_list and field not in result:
                result[field] = inverted[field]

        return result

    @api.model
    def _names_order_default(self):
        return 'last_first'

    @api.model
    def _get_names_order(self):
        """Get names order configuration from system parameters.
        You can override this method to read configuration from language,
        country, company or other"""
        return self.env['ir.config_parameter'].get_param(
            'partner_names_order', self._names_order_default())

    @api.model
    def _get_computed_name(self, lastname, firstname, middlename):
        """Compute the 'name' field according to splitted data.
        You can override this method to change the order of lastname and
        firstname the computed name"""
        return u" ".join((p for p in (firstname, middlename, lastname) if p))

    @api.multi
    @api.depends("firstname", "middlename", "lastname")
    def _compute_name(self):
        """Write the 'name' field according to splitted data."""
        for record in self:
            record.name = record._get_computed_name(record.lastname, record.firstname, record.middlename)

    @api.model
    def _get_inverse_name(self, name, is_company=False):
        parts = [name or False, False, False]

        return {"firstname": parts[0], "middlename": parts[1], "lastname": parts[2]}

    @api.multi
    def _inverse_name(self):
        """Try to revert the effect of :meth:`._compute_name`."""
        for record in self:
            parts = record._get_inverse_name(record.name, record.is_company)
            record.firstname = parts['firstname']
            record.middlename = parts['middlename']
            record.lastname = parts['lastname']

    @api.multi
    @api.constrains("firstname", "lastname", "middlename")
    def _check_name(self):
        """Ensure at least one name is set."""
        for record in self:
            if all((
                    record.type == 'contact' or record.is_company,
                    not (record.firstname or record.lastname or record.middlename)
            )):
                raise exceptions.EmptyNamesError(record)

    @api.onchange("firstname", "lastname", "middlename")
    def _onchange_subnames(self):
        """Avoid recursion when the user changes one of these fields.

        This forces to skip the :attr:`~.name` inversion when the user is
        setting it in a not-inverted way.
        """
        # Modify self's context without creating a new Environment.
        # See https://github.com/odoo/odoo/issues/7472#issuecomment-119503916.
        self.env.context = self.with_context(skip_onchange=True).env.context

    @api.onchange("name")
    def _onchange_name(self):
        """Ensure :attr:`~.name` is inverted in the UI."""
        if self.env.context.get("skip_onchange"):
            # Do not skip next onchange
            self.env.context = (
                self.with_context(skip_onchange=False).env.context)
        # else:
        #     self._inverse_name_after_cleaning_whitespace()

    @api.model
    def _install_partner_fullname(self):
        """Save names correctly in the database.

        Before installing the module, field ``name`` contains all full names.
        When installing it, this method parses those names and saves them
        correctly into the database. This can be called later too if needed.
        """
        # Find records with empty firstname and lastname
        records = self.search([("firstname", "=", False),
                               ("middlename", "=", False),
                               ("lastname", "=", False),
                               ])

        # Force calculations there
        records._inverse_name()
        _logger.info("%d partners updated installing module.", len(records))

    # Disabling SQL constraint givint a more explicit error using a Python
    # contstraint
    _sql_constraints = [(
        'check_name',
        "CHECK( 1=1 )",
        'Contacts require a name.'
    )]
