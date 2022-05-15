odoo.define('gbs_samuda_petty_cash.samudaReconciliationTags', function(require){
    "use strict";
    var core = require('web.core');
    var _t = core._t;
    var FieldMany2ManyTags = core.form_widget_registry.get('many2many_tags');
    var FieldMany2One = core.form_widget_registry.get('many2one');
    var accountReconciliation = require('account.reconciliation');
    var samudaReconciliation = accountReconciliation.abstractReconciliation.include({

        start: function() {
            this.create_form_fields['department_id'] = {
                id: "department_id",
                index: 50,
                corresponding_property: "department_id",
                label: _t("Department"),
                required: false,
                constructor: FieldMany2One,
                field_properties: {
                    relation: "hr.department",
                    string: _t("Department"),
                    type: "many2one",
                },
            };

            this.create_form_fields['cost_center_id'] = {
                id: "cost_center_id",
                index: 55,
                corresponding_property: "cost_center_id",
                label: _t("Cost Center"),
                required: false,
                constructor: FieldMany2One,
                field_properties: {
                    relation: "account.cost.center",
                    string: _t("Cost Center"),
                    type: "many2one",
                },
            };

            this.create_form_fields['operating_unit_id'] = {
                id: "operating_unit_id",
                index: 55,
                corresponding_property: "operating_unit_id",
                label: _t("Operating Unit"),
                required: false,
                constructor: FieldMany2One,
                field_properties: {
                    relation: "operating.unit",
                    string: _t("Operating Unit"),
                    type: "many2one",
                },
            };

            return this._super();
        },

        fetchPresets: function() {
            var self = this;
            var deferred_last_update = self.model_presets.query(['write_date']).order_by('-write_date').first().then(function (data) {
                self.presets_last_write_date = (data ? data.write_date : undefined);
            });
            var deferred_presets = self.model_presets.query().order_by('-sequence', '-id').all().then(function (data) {
                self.presets = {};
                _(data).each(function(datum){
                    var preset = {
                        id: datum.id,
                        name: datum.name,
                        sequence: datum.sequence,
                        lines: [{
                            account_id: datum.account_id,
                            journal_id: datum.journal_id,
                            label: datum.label,
                            amount_type: datum.amount_type,
                            amount: datum.amount,
                            tax_id: datum.tax_id,
                            analytic_account_id: datum.analytic_account_id,
                            department_id: datum.department_id,
                            cost_center_id: datum.cost_center_id,
                            department_id: datum.department_id,
                            operating_unit_id: datum.operating_unit_id
//                            receipt_status: datum.receipt_status
                        }]
                    };
                    if (datum.has_second_line) {
                        preset.lines.push({
                            account_id: datum.second_account_id,
                            journal_id: datum.second_journal_id,
                            label: datum.second_label,
                            amount_type: datum.second_amount_type,
                            amount: datum.second_amount,
                            tax_id: datum.second_tax_id,
                            analytic_account_id: datum.second_analytic_account_id,
                            department_id: datum.second_department_id,
                            cost_center_id: datum.second_cost_center_id,
                            operating_unit_id: datum.second_operating_unit_id
//                            receipt_status: datum.second_receipt_status
                        });
                    }
                    self.presets[datum.id] = preset;
                });
            });
            return $.when(deferred_last_update, deferred_presets);
        },

    });

    // store the department id to the new account move line
    var samudaReconciliationLine = accountReconciliation.abstractReconciliationLine.include({
        prepareCreatedMoveLinesForPersisting: function(lines) {
            var dicts = this._super(lines);
            for (var i=0; i<dicts.length; i++) {
                if (lines[i].department_id) dicts[i]['department_id'] = lines[i].department_id;
                if (lines[i].cost_center_id) dicts[i]['cost_center_id'] = lines[i].cost_center_id;
                if (lines[i].operating_unit_id) dicts[i]['operating_unit_id'] = lines[i].operating_unit_id;
            }
            return dicts;
        },


    });

})
