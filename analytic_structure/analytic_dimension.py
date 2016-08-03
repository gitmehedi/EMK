# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 XCG Consulting (www.xcg-consulting.fr)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import api, models, fields, _
from openerp.addons.oemetasl import OEMetaSL
from openerp.tools import config
from openerp.exceptions import ValidationError


DIMENSION_DUPLICATE_ERROR = _("Both {model1} and {model2} reference {dim}")
NO_MODEL_FOR_DIMENSION_ERROR = _("No model matches dimension {dim}")


def check_dimension_duplicate(models_by_dimension, dim_name, model_name):
    """Used by analytic_dimension.sync_analytic_codes_action.
    Make sure that dim_name is not a key in models_by_dimension.
    If the value is present, that would indicate that two different models
    define dimensions with the same name so we can't decide which model
    we want to use to sync analytic codes.

    tl;dr Raises ValidationError of dim_name is a key of models_by_dimension.

    :param models_by_dimension: dict, mapping from dimension names to
        model names.

    :param dim_name: str, name of a dimension

    :param mode_name: str, name of a model that references dim_name.

    :raises: ValidationError
    """
    if dim_name in models_by_dimension:
        model1 = model_name
        model2 = models_by_dimension[dim_name]
        raise ValidationError(_(DIMENSION_DUPLICATE_ERROR).format(
            model1=model1, model2=model2, dim=dim_name)
        )


class _dimension_meta(OEMetaSL):

    def __new__(cls, name, bases, nmspc):

        size = int(config.get_misc('analytic', 'analytic_size', 5))
        for n in xrange(1, size + 1):
            nmspc['ns{}_id'.format(n)] = fields.One2many(
                'analytic.structure',
                'nd_id',
                "Generated Subset of Structures",
                domain=[('ordering', '=', n)],
                auto_join=True,
            )
        return super(_dimension_meta, cls).__new__(cls, name, bases, nmspc)


class analytic_dimension(models.Model):

    __metaclass__ = _dimension_meta
    _name = 'analytic.dimension'
    _description = u"Analytic Dimension"

    name = fields.Char(
        string=u"Name",
        size=128,
        translate=config.get_misc('analytic', 'translate', False),
        required=True,
    )

    nc_ids = fields.One2many(
        comodel_name='analytic.code',
        inverse_name='nd_id',
        string=u"Codes")

    ns_id = fields.One2many(
        comodel_name='analytic.structure',
        inverse_name='nd_id',
        string=u"Structures")

    _sql_constraints = [
        ('unique_name', 'unique(name)', u"Name must be unique"),
    ]

    @api.multi
    def sync_analytic_codes_action(self):
        """Create missing analytic codes"""
        registry = self.env.registry
        dimension_models = [
            (name, model) for name, model in registry.iteritems()
            if getattr(model, '_dimension', None)
        ]

        # Dimension name => model object
        models_by_dimension = {}
        # Dimension name => analytic.code m2o field name
        column_by_name = {}
        # Place dimension info into dicts for easy retrieval
        for model_name, model in dimension_models:
            dim_config = getattr(model, '_dimension')
            if isinstance(dim_config, dict):
                dim_name = dim_config.get('name')
                column_name = dim_config.get('column', 'analytic_id')
            else:
                dim_name = dim_config
                column_name = 'analytic_id'

            check_dimension_duplicate(
                models_by_dimension, dim_name, model_name
            )
            models_by_dimension[dim_name] = model_name
            column_by_name[dim_name] = column_name

        for record in self:
            dimension_name = record.name

            if dimension_name not in models_by_dimension:
                raise ValidationError(
                    _(NO_MODEL_FOR_DIMENSION_ERROR).format(dim=dimension_name)
                )

            model_name = models_by_dimension[dimension_name]
            code_column = column_by_name[dimension_name]

            model_obj = self.env[model_name]

            # Look for records with missing analytic codes
            missing_code = model_obj.search([(code_column, '=', False)])
            # Create codes for those records using 'write' method
            # defined in MetaAnalytic.
            for dim_record in missing_code:
                dim_record.write({})
