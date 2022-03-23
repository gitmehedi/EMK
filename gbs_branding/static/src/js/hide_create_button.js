odoo.define('gbs_branding.hide_create_button', function (require) {
    "use strict";

    var core = require('web.core'),
        data = require('web.data'),
        Dialog = require('web.Dialog'),
        Model = require('web.Model'),
        form_relational = require('web.form_relational'),
        _t  = core._t;

    var ViewDialog = Dialog.extend({ // FIXME should use ViewManager
    /**
     *  options:
     *  -readonly: only applicable when not in creation mode, default to false
     * - alternative_form_view
     * - write_function
     * - read_function
     * - create_function
     * - parent_view
     * - child_name
     * - form_view_options
     */
    init: function(parent, options) {
        options = options || {};
        options.dialogClass = options.dialogClass || '';
        options.dialogClass += ' o_act_window';

        this._super(parent, $.extend(true, {}, options));

        this.res_model = options.res_model || null;
        this.res_id = options.res_id || null;
        this.domain = options.domain || [];
        this.context = options.context || {};
        this.options = _.extend(this.options || {}, options || {});

        this.on_selected = options.on_selected || (function() {});
    },

    init_dataset: function() {
        var self = this;
        this.created_elements = [];
        this.dataset = new data.ProxyDataSet(this, this.res_model, this.context);
        this.dataset.read_function = this.options.read_function;
        this.dataset.create_function = function(data, options, sup) {
            var fct = self.options.create_function || sup;
            return fct.call(this, data, options).done(function(r) {
                self.trigger('create_completed saved', r);
                self.created_elements.push(r);
            });
        };
        this.dataset.write_function = function(id, data, options, sup) {
            var fct = self.options.write_function || sup;
            return fct.call(this, id, data, options).done(function(r) {
                self.trigger('write_completed saved', r);
            });
        };
        this.dataset.parent_view = this.options.parent_view;
        this.dataset.child_name = this.options.child_name;

        this.on('closed', this, this.select);
    },

    select: function() {
        if (this.created_elements.length > 0) {
            this.on_selected(this.created_elements);
            this.created_elements = [];
        }
    }
});


    var SelectCreateDialog = ViewDialog.extend({
        custom_events: {
            get_controller_context: '_onGetControllerContext',
        },
        /**
         * options:
         * - initial_ids
         * - initial_view: form or search (default search)
         * - disable_multiple_selection
         * - list_view_options
         */
        init: function(parent, options) {
            this._super(parent, options);

            _.defaults(this.options, { initial_view: "search" });
            this.initial_ids = this.options.initial_ids;
        },

        open: function() {
            if(this.options.initial_view !== "search") {
                return this.create_edit_record();
            }

            var _super = this._super.bind(this);
            this.init_dataset();
            var context = pyeval.sync_eval_domains_and_contexts({
                domains: [],
                contexts: [this.context]
            }).context;
            var search_defaults = {};
            _.each(context, function (value_, key) {
                var match = /^search_default_(.*)$/.exec(key);
                if (match) {
                    search_defaults[match[1]] = value_;
                }
            });
            data_manager
                .load_views(this.dataset, [[false, 'list'], [false, 'search']], {})
                .then(this.setup.bind(this, search_defaults))
                .then(function (fragment) {
                    _super().$el.append(fragment);
                });
            return this;
        },

        setup: function(search_defaults, fields_views) {
            var self = this;
            if (this.searchview) {
                this.searchview.destroy();
            }
            var fragment = document.createDocumentFragment();
            var $header = $('<div/>').addClass('o_modal_header').appendTo(fragment);
            var $pager = $('<div/>').addClass('o_pager').appendTo($header);
            var options = {
                $buttons: $('<div/>').addClass('o_search_options').appendTo($header),
                search_defaults: search_defaults,
            };

            this.searchview = new SearchView(this, this.dataset, fields_views.search, options);
            this.searchview.on('search_data', this, function(domains, contexts, groupbys) {
                if (this.initial_ids) {
                    this.do_search(domains.concat([[["id", "in", this.initial_ids]], this.domain]),
                        contexts.concat(this.context), groupbys);
                    this.initial_ids = undefined;
                } else {
                    this.do_search(domains.concat([this.domain]), contexts.concat(this.context), groupbys);
                }
            });
            return this.searchview.prependTo($header).then(function() {
                self.searchview.toggle_visibility(true);

                self.view_list = new SelectCreateListView(self,
                    self.dataset, fields_views.list,
                    _.extend({'deletable': false,
                        'selectable': !self.options.disable_multiple_selection,
                        'import_enabled': false,
                        '$buttons': self.$buttons,
                        'disable_editable_mode': true,
                        'pager': true,
                    }, self.options.list_view_options || {}));
                self.view_list.on('edit:before', self, function (e) {
                    e.cancel = true;
                });
                self.view_list.popup = self;
                self.view_list.on('list_view_loaded', self, function() {
                    this.on_view_list_loaded();
                });

                var buttons = [
                    {text: _t("Cancel"), classes: "btn-default o_form_button_cancel", close: true}
                ];
                /*if(!self.options.no_create) {
                    buttons.splice(0, 0, {text: _t("Create"), classes: "btn-primary", click: function() {
                        self.creaF7te_edit_record();
                    }});
                }*/
                if(!self.options.disable_multiple_selection) {
                    buttons.splice(0, 0, {text: _t("Select"), classes: "btn-primary o_selectcreatepopup_search_select", disabled: true, close: true, click: function() {
                        self.on_selected(self.selected_ids);
                    }});
                }
                self.set_buttons(buttons);

                return self.view_list.appendTo(fragment).then(function() {
                    self.view_list.do_show();
                    self.view_list.render_pager($pager);
                    if (self.options.initial_facet) {
                        self.searchview.query.reset([self.options.initial_facet], {
                            preventSearch: true,
                        });
                    }
                    self.searchview.do_search();

                    return fragment;
                });
            });
        },
        do_search: function(domains, contexts, groupbys) {
            var results = pyeval.sync_eval_domains_and_contexts({
                domains: domains || [],
                contexts: contexts || [],
                group_by_seq: groupbys || []
            });
            this.view_list.do_search(results.domain, results.context, results.group_by);
        },
        on_click_element: function(ids) {
            this.selected_ids = ids || [];
            this.$footer.find(".o_selectcreatepopup_search_select").prop('disabled', this.selected_ids.length <= 0);
        },
        create_edit_record: function() {
            this.close();
            return new FormViewDialog(this.__parentedParent, this.options).open();
        },
        on_view_list_loaded: function() {},

        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------

        /**
         * Handles a context request: provides to the caller the context of the
         * list view.
         *
         * @private
         * @param {OdooEvent} ev
         * @param {function} ev.data.callback used to send the requested context
         */
        _onGetControllerContext: function (ev) {
            var context = this.view_list.get_context();
            ev.data.callback(context);
        },
    });

//    var FieldMany2One = core.form_widget_registry.get('many2one');
//
//    FieldMany2One.include({
//         _search_create_popup: function(view, ids, context) {
//            var self = this;
//            alert('Working!')
//        },
//    });

return {
    ViewDialog: ViewDialog,
    SelectCreateDialog: SelectCreateDialog,
};
});