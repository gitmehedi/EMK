# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.exceptions import AccessError, MissingError

import logging

_logger = logging.getLogger(__name__)

EXCLUDED_FIELDS = set((
    'report_sxw_content', 'report_rml_content', 'report_sxw', 'report_rml',
    'report_sxw_content_data', 'report_rml_content_data', 'search_view',))

ACTION_SLOTS = [
    "client_action_multi",  # sidebar wizard action
    "client_print_multi",  # sidebar report printing button
    "client_action_relate",  # sidebar related link
    "tree_but_open",  # double-click on item in tree view
    "tree_but_action",  # deprecated: same as tree_but_open
]


class ir_actions_server(models.Model):
    _inherit = 'ir.actions.server'

    groups_id = fields.Many2many('res.groups', string='Groups')


class ir_values(models.Model):
    _inherit = 'ir.values'

    @api.model
    @tools.ormcache_context('self._uid', 'action_slot', 'model', 'res_id', keys=('lang',))
    def get_actions(self, action_slot, model, res_id=False):
        """Retrieves the list of actions bound to the given model's action slot.
           See the class description for more details about the various action
           slots: :class:`~.ir_values`.

           :param string action_slot: the action slot to which the actions should be
                                      bound to - one of ``client_action_multi``,
                                      ``client_print_multi``, ``client_action_relate``,
                                      ``tree_but_open``.
           :param string model: model name
           :param int res_id: optional record id - will bind the action only to a
                              specific record of the model, not all records.
           :return: list of action tuples of the form ``(id, name, action_def)``,
                    where ``id`` is the ID of the default entry, ``name`` is the
                    action label, and ``action_def`` is a dict containing the
                    action definition as obtained by calling
                    :meth:`~odoo.models.Model.read` on the action record.
        """
        assert action_slot in ACTION_SLOTS, 'Illegal action slot value: %s' % action_slot
        # use a direct SQL query for performance reasons,
        # this is called very often
        query = """ SELECT v.id, v.name, v.value FROM ir_values v
                        WHERE v.key = %s AND v.key2 = %s AND v.model = %s
                            AND (v.res_id = %s OR v.res_id IS NULL OR v.res_id = 0)
                        ORDER BY v.id """
        self._cr.execute(query, ('action', action_slot, model, res_id or None))

        # map values to their corresponding action record
        actions = []
        for id, name, value in self._cr.fetchall():
            if not value:
                continue  # skip if undefined
            action_model, action_id = value.split(',')
            if action_model not in self.env:
                continue  # unknown model? skip it!
            action = self.env[action_model].browse(int(action_id))
            actions.append((id, name, action))

        # process values and their action
        results = {}
        for id, name, action in actions:
            fields = [field for field in action._fields if field not in EXCLUDED_FIELDS]
            # FIXME: needs cleanup
            try:
                action_def = {
                    field: action._fields[field].convert_to_read(action[field], action)
                    for field in fields
                }
                if action._name in ('ir.actions.report.xml', 'ir.actions.act_window', 'ir.actions.server'):
                    if action.groups_id and not action.groups_id & self.env.user.groups_id:
                        if name == 'Menuitem':
                            raise AccessError(_('You do not have the permission to perform this operation!!!'))
                        continue
                # keep only the last action registered for each action name
                results[name] = (id, name, action_def)
            except (AccessError, MissingError):
                continue
        return sorted(results.values())

