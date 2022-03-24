odoo.define("gbs_branding.custom_js", function (require) {
    "use strict";

    var Form_common = require('web.form_common');

    var core = require('web.core');
    var ListView = require('web.ListView');
    var SearchView = require('web.SearchView');

    var QWeb = core.qweb;
    var _t = core._t;

    var SelectCreateListView = ListView.extend({
        do_add_record: function () {
            this.popup.create_edit_record();
        },
        select_record: function(index) {
            this.popup.on_selected([this.dataset.ids[index]]);
            this.popup.close();
        },
        do_select: function(ids, records) {
            this._super.apply(this, arguments);
            this.popup.on_click_element(ids);
        }
    });

    Form_common.SelectCreateDialog.include({

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
                // [Start] Genweb2: custom change for removing create button

    //            if(!self.options.no_create) {
    //                buttons.splice(0, 0, {text: _t("Create"), classes: "btn-primary", click: function() {
    //                    self.create_edit_record();
    //                }});
    //            }

                // [End] Genweb2:
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
    })
});
