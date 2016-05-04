function openerp_pos_promotion_loyalty(instance, module) { // module is
    // instance.point_of_sale
    var QWeb = instance.web.qweb;
    var _t = instance.web._t;

    var round_di = instance.web.round_decimals;
    var round_pr = instance.web.round_precision;

    // The PosModel contains the Point Of Sale's representation of the backend.
    // Since the PoS must work in standalone ( Without connection to the server
    // )
    // it must contains a representation of the server's PoS backend.
    // (taxes, product list, configuration options, etc.) this representation
    // is fetched and stored by the PosModel at the initialisation.
    // this is done asynchronously, a ready deferred alows the GUI to wait
    // interactively
    // for the loading to be completed
    // There is a single instance of the PosModel for each Front-End instance,
    // it is usually called
    // 'pos' and is available to all widgets extending PosWidget.

    module.PosModel = Backbone.Model
        .extend({
            initialize: function (session, attributes) {
                Backbone.Model.prototype.initialize.call(this, attributes);
                var self = this;
                this.session = session;
                this.flush_mutex = new $.Mutex(); // used to make sure the
                // orders are sent to
                // the server once at
                // time
                this.pos_widget = attributes.pos_widget;

                this.proxy = new module.ProxyDevice(this); // used to
                // communicate
                // to the
                // hardware
                // devices via a
                // local proxy
                this.barcode_reader = new module.BarcodeReader({
                    'pos': this,
                    proxy: this.proxy,
                    patterns: {}
                }); // used to read barcodes
                this.proxy_queue = new module.JobQueue(); // used to
                // prevent
                // parallels
                // communications
                // to the proxy
                this.db = new module.PosDB(); // a local database used to
                // search trough products
                // and categories & store
                // pending orders

                // search trough products
                // and categories & store
                // pending orders

                // Created by Mithun
                // Create the new instance of ClientListScreenWidget module
                // globally
                this.clientDetail = new module.ClientListScreenWidget(this,
                    {});

                this.debug = jQuery.deparam(jQuery.param.querystring()).debug !== undefined; // debug
                // mode
                // Business data; loaded from the server at launch
                this.accounting_precision = 2; // TODO
                this.company_logo = null;
                this.company_logo_base64 = '';
                this.currency = null;
                this.shop = null;
                this.company = null;
                this.user = null;
                this.users = [];
                this.partners = [];
                this.cashier = null;
                this.cashregisters = [];
                this.bankstatements = [];
                this.taxes = [];
                this.pos_session = null;
                this.config = null;
                this.units = [];
                this.units_by_id = {};
                this.pricelist = null;
                this.order_sequence = 1;
                // loyalty rules
                this.loyalty_rules = [];
                this.redemption_rules = [];

                window.posmodel = this;

                // these dynamic attributes can be watched for change by
                // other models or widgets
                this.set({
                    'synch': {
                        state: 'connected',
                        pending: 0
                    },
                    'orders': new module.OrderCollection(),
                    'selectedOrder': null,
                });

                this.bind('change:synch', function (pos, synch) {
                    clearTimeout(self.synch_timeout);
                    self.synch_timeout = setTimeout(function () {
                        if (synch.state !== 'disconnected'
                            && synch.pending > 0) {
                            self.set('synch', {
                                state: 'disconnected',
                                pending: synch.pending
                            });
                        }
                    }, 3000);
                });

                this.get('orders').bind(
                    'remove',
                    function (order, _unused_, options) {
                        self.on_removed_order(order, options.index,
                            options.reason);
                    });

                // We fetch the backend data on the server asynchronously.
                // this is done only when the pos user interface is
                // launched,
                // Any change on this data made on the server is thus not
                // reflected on the point of sale until it is relaunched.
                // when all the data has loaded, we compute some stuff, and
                // declare the Pos ready to be used.
                this.ready = this.load_server_data().then(function () {
                    if (self.config.use_proxy) {
                        return self.connect_to_proxy();
                    }
                });

            },

            // releases ressources holds by the model at the end of life of
            // the posmodel
            destroy: function () {
                // FIXME, should wait for flushing, return a deferred to
                // indicate successfull destruction
                // this.flush();
                this.proxy.close();
                this.barcode_reader.disconnect();
                this.barcode_reader.disconnect_from_proxy();
            },
            connect_to_proxy: function () {
                var self = this;
                var done = new $.Deferred();
                this.barcode_reader.disconnect_from_proxy();
                this.pos_widget.loading_message(
                    _t('Connecting to the PosBox'), 0);
                this.pos_widget.loading_skip(function () {
                    self.proxy.stop_searching();
                });
                this.proxy.autoconnect({
                    force_ip: self.config.proxy_ip || undefined,
                    progress: function (prog) {
                        self.pos_widget.loading_progress(prog);
                    },
                }).then(function () {
                    if (self.config.iface_scan_via_proxy) {
                        self.barcode_reader.connect_to_proxy();
                    }
                }).always(function () {
                    done.resolve();
                });
                return done;
            },

            // helper function to load data from the server. Obsolete use
            // the models loader below.
            fetch: function (model, fields, domain, ctx) {
                this._load_progress = (this._load_progress || 0) + 0.05;
                this.pos_widget.loading_message(
                    _t('Loading') + ' ' + model, this._load_progress);
                return new instance.web.Model(model).query(fields).filter(
                    domain).context(ctx).all()
            },

            // Server side model loaders. This is the list of the models
            // that need to be loaded from
            // the server. The models are loaded one by one by this list's
            // order. The 'loaded' callback
            // is used to store the data in the appropriate place once it
            // has been loaded. This callback
            // can return a deferred that will pause the loading of the next
            // module.
            // a shared temporary dictionary is available for loaders to
            // communicate private variables
            // used during loading such as object ids, etc.
            models: [
                {
                    model: 'res.users',
                    fields: ['name', 'company_id'],
                    ids: function (self) {
                        return [self.session.uid];
                    },
                    loaded: function (self, users) {
                        self.user = users[0];
                    },
                },
                {
                    model: 'res.company',
                    fields: ['currency_id', 'email', 'website',
                        'company_registry', 'vat', 'name', 'phone',
                        'partner_id', 'country_id',
                        'tax_calculation_rounding_method'],
                    ids: function (self) {
                        return [self.user.company_id[0]]
                    },
                    loaded: function (self, companies) {
                        self.company = companies[0];
                    },
                },
                {
                    model: 'decimal.precision',
                    fields: ['name', 'digits'],
                    loaded: function (self, dps) {
                        self.dp = {};
                        for (var i = 0; i < dps.length; i++) {
                            self.dp[dps[i].name] = dps[i].digits;
                        }
                    },
                },
                {
                    model: 'product.uom',
                    fields: [],
                    domain: null,
                    context: function (self) {
                        return {
                            active_test: false
                        };
                    },
                    loaded: function (self, units) {
                        self.units = units;
                        var units_by_id = {};
                        for (var i = 0, len = units.length; i < len; i++) {
                            units_by_id[units[i].id] = units[i];
                            units[i].groupable = (units[i].category_id[0] === 1);
                            units[i].is_unit = (units[i].id === 1);
                        }
                        self.units_by_id = units_by_id;
                    }
                },
                {
                    model: 'res.users',
                    fields: ['name', 'ean13'],
                    domain: null,
                    loaded: function (self, users) {
                        self.users = users;
                    },
                },
                {
                    model: 'res.partner',
                    fields: ['name', 'street', 'city', 'state_id',
                        'country_id', 'vat', 'phone', 'zip',
                        'mobile', 'email', 'ean13', 'write_date',
                        'point_loyalty', 'category_id'],
                    domain: [['customer', '=', true]],
                    loaded: function (self, partners) {
                        self.partners = partners;
                        self.db.add_partners(partners);
                    },
                },
                {
                    model: 'res.country',
                    fields: ['name'],
                    loaded: function (self, countries) {
                        self.countries = countries;
                        self.company.country = null;
                        for (var i = 0; i < countries.length; i++) {
                            if (countries[i].id === self.company.country_id[0]) {
                                self.company.country = countries[i];
                            }
                        }
                    },
                },
                {
                    model: 'account.tax',
                    fields: ['name', 'amount', 'price_include',
                        'include_base_amount', 'type', 'child_ids',
                        'child_depend', 'include_base_amount'],
                    domain: null,
                    loaded: function (self, taxes) {
                        self.taxes = taxes;
                        self.taxes_by_id = {};
                        _.each(taxes, function (tax) {
                            self.taxes_by_id[tax.id] = tax;
                        });
                        _
                            .each(
                                self.taxes_by_id,
                                function (tax) {
                                    tax.child_taxes = {};
                                    _
                                        .each(
                                            tax.child_ids,
                                            function (child_tax_id) {
                                                tax.child_taxes[child_tax_id] = self.taxes_by_id[child_tax_id];
                                            });
                                });
                    },
                },
                {
                    model: 'pos.session',
                    fields: ['id', 'journal_ids', 'name', 'user_id',
                        'config_id', 'start_at', 'stop_at',
                        'sequence_number', 'login_number'],
                    domain: function (self) {
                        return [['state', '=', 'opened'],
                            ['user_id', '=', self.session.uid]];
                    },
                    loaded: function (self, pos_sessions) {
                        self.pos_session = pos_sessions[0];

                        var orders = self.db.get_orders();
                        for (var i = 0; i < orders.length; i++) {
                            self.pos_session.sequence_number = Math
                                .max(
                                    self.pos_session.sequence_number,
                                    orders[i].data.sequence_number + 1);
                        }
                    },
                },
                {
                    model: 'pos.config',
                    fields: [],
                    domain: function (self) {
                        return [['id', '=',
                            self.pos_session.config_id[0]]];
                    },
                    loaded: function (self, configs) {
                        self.config = configs[0];
                        self.config.use_proxy = self.config.iface_payment_terminal
                            || self.config.iface_electronic_scale
                            || self.config.iface_print_via_proxy
                            || self.config.iface_scan_via_proxy
                            || self.config.iface_cashdrawer;

                        self.barcode_reader.add_barcode_patterns({
                            'product': self.config.barcode_product,
                            'cashier': self.config.barcode_cashier,
                            // 'client': self.config.barcode_customer,
                            'weight': self.config.barcode_weight,
                            'discount': self.config.barcode_discount,
                            'price': self.config.barcode_price,
                        });

                        if (self.config.company_id[0] !== self.user.company_id[0]) {
                            throw new Error(
                                _t("Error: The Point of Sale User must belong to the same company as the Point of Sale. You are probably trying to load the point of sale as an administrator in a multi-company setup, with the administrator account set to the wrong company."));
                        }
                    },
                },
                {
                    model: 'stock.location',
                    fields: [],
                    ids: function (self) {
                        return [self.config.stock_location_id[0]];
                    },
                    loaded: function (self, locations) {
                        self.shop = locations[0];
                    },
                },
                {
                    model: 'product.pricelist',
                    fields: ['currency_id'],
                    ids: function (self) {
                        return [self.config.pricelist_id[0]];
                    },
                    loaded: function (self, pricelists) {
                        self.pricelist = pricelists[0];
                    },
                },
                {
                    model: 'res.currency',
                    fields: ['name', 'symbol', 'position',
                        'rounding', 'accuracy'],
                    ids: function (self) {
                        return [self.pricelist.currency_id[0]];
                    },
                    loaded: function (self, currencies) {
                        self.currency = currencies[0];
                        if (self.currency.rounding > 0) {
                            self.currency.decimals = Math.ceil(Math
                                    .log(1.0 / self.currency.rounding)
                                / Math.log(10));
                        } else {
                            self.currency.decimals = 0;
                        }

                    },
                },
                {
                    model: 'product.packaging',
                    fields: ['ean', 'product_tmpl_id'],
                    domain: null,
                    loaded: function (self, packagings) {
                        self.db.add_packagings(packagings);
                    },
                },
                {
                    model: 'pos.category',
                    fields: ['id', 'name', 'parent_id', 'child_id', 'code',
                        'image'],
                    domain: null,
                    loaded: function (self, categories) {
                        self.db.add_categories(categories);
                    },
                },
                {
                    model: 'product.product',
                    fields: ['display_name', 'list_price', 'price',
                        'pos_categ_id', 'taxes_id', 'ean13',
                        'default_code', 'to_weight', 'uom_id',
                        'uos_id', 'uos_coeff', 'mes_type',
                        'description_sale', 'description',
                        'product_tmpl_id', 'categ_id'],
                    domain: [['sale_ok', '=', true],
                        ['available_in_pos', '=', true]],
                    context: function (self) {
                        return {
                            pricelist: self.pricelist.id,
                            display_default_code: false
                        };
                    },
                    loaded: function (self, products) {
                        self.db.add_products(products);
                    },
                },
                {
                    model: 'account.bank.statement',
                    fields: ['account_id', 'currency', 'journal_id',
                        'state', 'name', 'user_id',
                        'pos_session_id'],
                    domain: function (self) {
                        return [
                            ['state', '=', 'open'],
                            ['pos_session_id', '=',
                                self.pos_session.id]];
                    },
                    loaded: function (self, bankstatements, tmp) {
                        self.bankstatements = bankstatements;

                        tmp.journals = [];
                        _.each(bankstatements, function (statement) {
                            tmp.journals.push(statement.journal_id[0]);
                        });
                    },
                },
                {
                    model: 'account.journal',
                    fields: [],
                    domain: function (self, tmp) {
                        return [['id', 'in', tmp.journals]];
                    },
                    loaded: function (self, journals) {
                        self.journals = journals;

                        // associate the bank statements with their
                        // journals.
                        var bankstatements = self.bankstatements;
                        for (var i = 0, ilen = bankstatements.length; i < ilen; i++) {
                            for (var j = 0, jlen = journals.length; j < jlen; j++) {
                                if (bankstatements[i].journal_id[0] === journals[j].id) {
                                    bankstatements[i].journal = journals[j];
                                }
                            }
                        }
                        self.cashregisters = bankstatements;
                    },
                },
                {
                    model: 'loyalty.rule',
                    fields: [],
                    loaded: function (self, loyalty_rule) {
                        self.loyalty_rules = loyalty_rule;
                    },
                },
                {
                    model: 'redemption.rule',
                    fields: [],
                    loaded: function (self, redemption_rule) {
                        self.redemption_rules = redemption_rule;
                    },
                }, {
                    model: 'promos.rules',
                    fields: [],
                    loaded: function (self, promotion_rules) {
                        self.promotion_rules = promotion_rules;
                    }
                }, {
                    model: 'promos.rules.conditions.exps',
                    fields: [],
                    loaded: function (self, promos_rules_conditions_exps) {
                        self.promos_rules_conditions_exps = promos_rules_conditions_exps;
                    }
                }, {
                    model: 'promos.rules.actions',
                    fields: [],
                    loaded: function (self, promos_rules_actions) {
                        self.promos_rules_actions = promos_rules_actions;
                    }
                }, {
                    model: 'res.partner.category',
                    fields: [],
                    loaded: function (self, res_partner_category) {
                        self.res_partner_category = res_partner_category;
                    }
                }, {
                    model: 'promotion.groups',
                    fields: [],
                    loaded: function (self, promotion_groups) {
                        self.promotion_groups = promotion_groups;
                    }
                },
                {
                    label: 'fonts',
                    loaded: function (self) {
                        var fonts_loaded = new $.Deferred();

                        // Waiting for fonts to be loaded to prevent
                        // receipt printing
                        // from printing empty receipt while loading
                        // Inconsolata
                        // ( The font used for the receipt )
                        waitForWebfonts(['Lato', 'Inconsolata'],
                            function () {
                                fonts_loaded.resolve();
                            });

                        // The JS used to detect font loading is not
                        // 100% robust, so
                        // do not wait more than 5sec
                        setTimeout(function () {
                            fonts_loaded.resolve();
                        }, 5000);

                        return fonts_loaded;
                    },
                },
                {
                    label: 'pictures',
                    loaded: function (self) {
                        self.company_logo = new Image();
                        var logo_loaded = new $.Deferred();
                        self.company_logo.onload = function () {
                            var img = self.company_logo;
                            var ratio = 1;
                            var targetwidth = 300;
                            var maxheight = 150;
                            if (img.width !== targetwidth) {
                                ratio = targetwidth / img.width;
                            }
                            if (img.height * ratio > maxheight) {
                                ratio = maxheight / img.height;
                            }
                            var width = Math.floor(img.width * ratio);
                            var height = Math.floor(img.height * ratio);
                            var c = document.createElement('canvas');
                            c.width = width;
                            c.height = height
                            var ctx = c.getContext('2d');
                            ctx.drawImage(self.company_logo, 0, 0,
                                width, height);

                            self.company_logo_base64 = c.toDataURL();
                            logo_loaded.resolve();
                        };
                        self.company_logo.onerror = function () {
                            logo_loaded.reject();
                        };
                        self.company_logo.crossOrigin = "anonymous";
                        self.company_logo.src = '/web/binary/company_logo'
                            + '?_' + Math.random();

                        return logo_loaded;
                    },
                },],

            // loads all the needed data on the sever. returns a deferred
            // indicating when all the data has loaded.
            load_server_data: function () {
                var self = this;
                var loaded = new $.Deferred();
                var progress = 0;
                var progress_step = 1.0 / self.models.length;

                var tmp = {}; // this is used to share a temporary state
                // between models loaders

                function load_model(index) {
                    if (index >= self.models.length) {
                        loaded.resolve();
                    } else {

                        var model = self.models[index];

                        self.pos_widget.loading_message(_t('Loading') + ' '
                            + (model.label || model.model || ''),
                            progress);
                        var fields = typeof model.fields === 'function' ? model
                            .fields(self, tmp)
                            : model.fields;
                        var domain = typeof model.domain === 'function' ? model
                            .domain(self, tmp)
                            : model.domain;
                        var context = typeof model.context === 'function' ? model
                            .context(self, tmp)
                            : model.context;
                        var ids = typeof model.ids === 'function' ? model
                            .ids(self, tmp) : model.ids;
                        progress += progress_step;

                        if (model.model) {
                            if (model.ids) {
                                var records = new instance.web.Model(
                                    model.model).call('read', [ids,
                                    fields], context);
                            } else {
                                var records = new instance.web.Model(
                                    model.model).query(fields).filter(
                                    domain).context(context).all()
                            }
                            records.then(function (result) {
                                try { // catching exceptions in
                                    // model.loaded(...)
                                    $.when(model.loaded(self, result, tmp))
                                        .then(function () {
                                            load_model(index + 1);
                                        }, function (err) {
                                            loaded.reject(err);
                                        });
                                } catch (err) {
                                    loaded.reject(err);
                                }
                            }, function (err) {
                                loaded.reject(err);
                            });
                        } else if (model.loaded) {
                            try { // catching exceptions in
                                // model.loaded(...)
                                $.when(model.loaded(self, tmp)).then(
                                    function () {
                                        load_model(index + 1);
                                    }, function (err) {
                                        loaded.reject(err);
                                    });
                            } catch (err) {
                                loaded.reject(err);
                            }
                        } else {
                            load_model(index + 1);
                        }
                    }
                }

                try {
                    load_model(0);
                } catch (err) {
                    loaded.reject(err);
                }

                return loaded;
            },

            // reload the list of partner, returns as a deferred that
            // resolves if there were
            // updated partners, and fails if not
            load_new_partners: function () {
                var self = this;
                var def = new $.Deferred();
                var fields = _.find(this.models, function (model) {
                    return model.model === 'res.partner';
                }).fields;
                new instance.web.Model('res.partner')

                    .query(fields).filter(
                    [['write_date', '>',
                        this.db.get_partner_write_date()]]).all({
                    'timeout': 3000,
                    'shadow': true
                }).then(function (partners) {
                    if (self.db.add_partners(partners)) { // check if the
                        // partners we
                        // got were real
                        // updates
                        def.resolve();
                    } else {
                        def.reject();
                    }
                }, function (err, event) {
                    event.preventDefault();
                    def.reject();
                });
                return def;
            },

            // this is called when an order is removed from the order
            // collection. It ensures that there is always an existing
            // order and a valid selected order
            on_removed_order: function (removed_order, index, reason) {
                if ((reason === 'abandon' || removed_order.temporary)
                    && this.get('orders').size() > 0) {
                    // when we intentionally remove an unfinished order, and
                    // there is another existing one
                    this.set({
                        'selectedOrder': this.get('orders').at(index)
                        || this.get('orders').last()
                    });
                } else {
                    // when the order was automatically removed after
                    // completion,
                    // or when we intentionally delete the only concurrent
                    // order
                    this.add_new_order();
                }
            },

            // creates a new empty order and sets it as the current order
            add_new_order: function () {
                var order = new module.Order({
                    pos: this
                });
                this.get('orders').add(order);
                this.set('selectedOrder', order);
            },

            get_order: function () {
                return this.get('selectedOrder');
            },

            // removes the current order
            delete_current_order: function () {
                this.get('selectedOrder').destroy({
                    'reason': 'abandon'
                });
            },
            processDate: function (date) {
                var parts = date.split("-");
                return new Date(parts[0], parts[1] - 1,
                    parts[2]);
            },


            // saves the order locally and try to send it to the backend.
            // it returns a deferred that succeeds after having tried to
            // send the order and all the other pending orders.
            push_order: function (order) {
                var self = this;

                if (order) {
                    this.proxy.log('push_order', order.export_as_JSON());
                    this.db.add_order(order.export_as_JSON());

                    var partner = order.get('client');
                    var loyaltyRule = order.get('pos').loyalty_rules;
                    if (loyaltyRule.length > 0 && partner != null) {

                        var loyaltyResult = 0;
                        var ruleArray = [];
                        var purchaseStr = "purchase amount";
                        var totalAmount = order.getSubtotal();
                        var minPurchase = 0;
                        var result = 0;
                        for (i = 0, ruleLength = loyaltyRule.length; i < ruleLength; i++) {
                            var rule = loyaltyRule[i];

                            if (rule.is_active == true
                                && rule.loyalty_basis == purchaseStr.trim()) {

                                var endDate = rule.end_date;
                                var startDate = rule.start_date;
                                var date = new Date();
                                var day = date.getDate();
                                var month = date.getMonth() + 1;
                                var year = date.getFullYear();
                                var today = year + '-' + month + '-' + day;
                                if (startDate <= endDate) {
                                    if (self.processDate(today) >= self.processDate(startDate)
                                        && self.processDate(today) <= self.processDate(endDate)) {
                                        minPurchase = rule.min_purchase;
                                        ruleArray.push(minPurchase);
                                    }
                                }
                            }

                        }

                        var sortedRule = ruleArray.sort(function (a, b) {
                            return a - b;
                        });

                        /*
                         -calculate loyalty point with existing loyalty point
                         */
                        if (sortedRule[0] != minPurchase) {
                            partner['point_loyalty'] = order
                                .getRewardToLoyaltyPoint();

                        } else {
                            var rewardToLoyaltyPoint = order
                                .getRewardToLoyaltyPoint();
                            var redemTotal = order.getRedemTotal();
                            //var dueTotal = order.getTotalTaxIncluded();
                            var dueTotal = order.getTotalWithTax();

                            var redemRemain = order.getRedemLeft();
                            if (minPurchase >= totalAmount) {
                                result = rewardToLoyaltyPoint;
                                partner['point_loyalty'] = result;
                            } else {
                                var pointUnit = rule.point_unit;
                                var purchaseUnitPerPoint = rule.purchase_unit_per_point;
                                loyaltyResult = (pointUnit * dueTotal)
                                    / purchaseUnitPerPoint;
                                result = loyaltyResult
                                    + rewardToLoyaltyPoint;
                                partner['point_loyalty'] = result;
                            }
                        }
                        self.db.add_partners(partner);
                        self.clientDetail.update_point_from_order(partner);
                    }
                }

                var pushed = new $.Deferred();

                this.flush_mutex.exec(function () {
                    var flushed = self._flush_orders(self.db.get_orders());

                    flushed.always(function (ids) {
                        pushed.resolve();
                    });
                });
                return pushed;
            },

            // saves the order locally and try to send it to the backend and
            // make an invoice
            // returns a deferred that succeeds when the order has been
            // posted and successfully generated
            // an invoice. This method can fail in various ways:
            // error-no-client: the order must have an associated
            // partner_id. You can retry to make an invoice once
            // this error is solved
            // error-transfer: there was a connection error during the
            // transfer. You can retry to make the invoice once
            // the network connection is up

            push_and_invoice_order: function (order) {
                var self = this;
                var invoiced = new $.Deferred();

                if (!order.get_client()) {
                    invoiced.reject('error-no-client');
                    return invoiced;
                }

                var order_id = this.db.add_order(order.export_as_JSON());

                this.flush_mutex.exec(function () {
                    var done = new $.Deferred(); // holds the mutex

                    // send the order to the server
                    // we have a 30 seconds timeout on this push.
                    // FIXME: if the server takes more than 30 seconds to
                    // accept the order,
                    // the client will believe it wasn't successfully sent,
                    // and very bad
                    // things will happen as a duplicate will be sent next
                    // time
                    // so we must make sure the server detects and ignores
                    // duplicated orders

                    var transfer = self._flush_orders([self.db
                        .get_order(order_id)], {
                        timeout: 30000,
                        to_invoice: true
                    });

                    transfer.fail(function () {
                        invoiced.reject('error-transfer');
                        done.reject();
                    });

                    // on success, get the order id generated by the server
                    transfer.pipe(function (order_server_id) {

                        // generate the pdf and download it
                        self.pos_widget.do_action(
                            'point_of_sale.pos_invoice_report', {
                                additional_context: {
                                    active_ids: order_server_id,
                                }
                            });

                        invoiced.resolve();
                        done.resolve();
                    });

                    return done;

                });

                return invoiced;
            },

            // wrapper around the _save_to_server that updates the synch
            // status widget
            _flush_orders: function (orders, options) {
                var self = this;

                this.set('synch', {
                    state: 'connecting',
                    pending: orders.length
                });

                return self._save_to_server(orders, options).done(
                    function (server_ids) {
                        var pending = self.db.get_orders().length;

                        self.set('synch', {
                            state: pending ? 'connecting'
                                : 'connected',
                            pending: pending
                        });

                        return server_ids;
                    });
            },

            // send an array of orders to the server
            // available options:
            // - timeout: timeout for the rpc call in ms
            // returns a deferred that resolves with the list of
            // server generated ids for the sent orders
            _save_to_server: function (orders, options) {
                if (!orders || !orders.length) {
                    var result = $.Deferred();
                    result.resolve([]);
                    return result;
                }

                options = options || {};

                var self = this;
                var timeout = typeof options.timeout === 'number' ? options.timeout
                    : 7500 * orders.length;

                // we try to send the order. shadow prevents a spinner if it
                // takes too long. (unless we are sending an invoice,
                // then we want to notify the user that we are waiting on
                // something )
                var posOrderModel = new instance.web.Model('pos.order');
                return posOrderModel
                    .call(
                        'create_from_ui',
                        [_
                            .map(
                                orders,
                                function (order) {
                                    order.to_invoice = options.to_invoice || false;
                                    return order;
                                })], undefined, {
                            shadow: !options.to_invoice,
                            timeout: timeout
                        })
                    .then(function (server_ids) {
                        _.each(orders, function (order) {
                            self.db.remove_order(order.id);
                        });
                        return server_ids;
                    })
                    .fail(
                        function (error, event) {
                            if (error.code === 200) { // Business
                                // Logic
                                // Error,
                                // not a
                                // connection
                                // problem
                                self.pos_widget.screen_selector
                                    .show_popup(
                                        'error-traceback',
                                        {
                                            message: error.data.message,
                                            comment: error.data.debug
                                        });
                            }
                            // prevent an error popup creation by
                            // the rpc failure
                            // we want the failure to be silent as
                            // we send the orders in the background
                            event.preventDefault();
                            console.error('Failed to send orders:',
                                orders);
                        });
            },

            scan_product: function (parsed_code) {
                var self = this;
                var selectedOrder = this.get('selectedOrder');
                if (parsed_code.encoding === 'ean13') {
                    var product = this.db
                        .get_product_by_ean13(parsed_code.base_code);
                } else if (parsed_code.encoding === 'reference') {
                    var product = this.db
                        .get_product_by_reference(parsed_code.code);
                }

                if (!product) {
                    return false;
                }

                if (parsed_code.type === 'price') {
                    selectedOrder.addProduct(product, {
                        price: parsed_code.value
                    });
                } else if (parsed_code.type === 'weight') {
                    selectedOrder.addProduct(product, {
                        quantity: parsed_code.value,
                        merge: false
                    });
                } else if (parsed_code.type === 'discount') {
                    selectedOrder.addProduct(product, {
                        discount: parsed_code.value,
                        merge: false
                    });
                } else {
                    selectedOrder.addProduct(product);
                }
                return true;
            },
        });
    module.Paymentline = module.Paymentline.extend({
        initialize: function (attributes, options) {
            this.amount = 0;
            this.cashregister = options.cashregister;
            this.name = this.cashregister.journal_id[1];
            this.is_redemption = this.cashregister.journal.is_redemption;
            this.selected = false;
            this.pos = options.pos;
        }
    });
    //only for promotion
    var orderline_id = 1;

    module.Orderline = module.Orderline.extend({

        initialize: function (attr, options) {
            this.pos = options.pos;
            this.order = options.order;
            this.product = options.product;
            this.price = options.product.price;
            this.set_quantity(1);
            this.discount = 0;
            this.discountStr = '0';
            this.type = 'unit';
            this.arguments = 0;
            this.selected = false;
            this.id = orderline_id++;
        },
        clone: function () {
            var orderline = new module.Orderline({}, {
                pos: this.pos,
                order: null,
                product: this.product,
                price: this.price,
            });
            orderline.quantity = this.quantity;
            orderline.quantityStr = this.quantityStr;
            orderline.discount = this.discount;
            orderline.type = this.type;
            orderline.selected = false;
            return orderline;
        },
        set_arguments: function (prodDiscPrice, actionType, arguments) {
            this.arguments = prodDiscPrice;
            if (actionType == 'prod_sub_disc_fix') {
                this.discountStr = 'fix amount: ' + arguments + '';

            } else if (actionType == 'prod_sub_disc_perc') {
                this.discountStr = ': ' + arguments + '%';
            }
            this.trigger('change', this);
        },
        get_arguments: function () {
            return this.arguments;
        },
        get_display_price: function () {
            return this.get_base_price();
        },

        get_base_price: function () {
            var rounding = this.pos.currency.rounding;
            var promosRulesActions = this.pos.promos_rules_actions;
            //var orderLine = this.discountAmount;
            if (promosRulesActions !== undefined && promosRulesActions.length > 0) {
                for (var n = 0, len = promosRulesActions.length; len > n; n++) {
                    if (promosRulesActions[n].action_type == 'prod_sub_disc_perc') {
                        return round_pr(((this.get_unit_price() * this.get_quantity()) - (this.get_discount())), rounding);
                    } else if (promosRulesActions[n].action_type == 'prod_sub_disc_fix') {
                        return round_pr(((this.get_unit_price() * this.get_quantity()) - this.get_arguments()), rounding);
                    } else if (promosRulesActions[n].action_type == 'cart_disc_perc' || promosRulesActions[n].action_type == 'cart_disc_fix') {
                        return round_pr((this.get_unit_price() * this.get_quantity()), rounding);
                    } else {
                        //return round_pr((this.get_unit_price() * this.get_quantity()) - (this.get_discount() * this.get_quantity()), rounding);
                        return round_pr(((this.get_unit_price() * this.get_quantity()) - (this.get_discount())), rounding);
                    }
                }
            } else {
                var rounding = this.pos.currency.rounding;
                return round_pr(this.get_unit_price() * this.get_quantity() * (1 - this.get_discount() / 100), rounding);
            }
        },

        get_all_prices: function () {
            //var base = round_pr(this.get_quantity() * this.get_unit_price() * (1.0 - (this.get_discount() / 100.0)), this.pos.currency.rounding);

            var base = round_pr((this.get_unit_price() * this.get_quantity()), this.pos.currency.rounding);
            var totalTax = base;
            var totalNoTax = base;
            var taxtotal = 0;

            var product = this.get_product();
            var taxes_ids = product.taxes_id;
            var taxes = this.pos.taxes;
            var taxdetail = {};
            var product_taxes = [];

            _(taxes_ids).each(function (el) {
                product_taxes.push(_.detect(taxes, function (t) {
                    return t.id === el;
                }));
            });

            var all_taxes = _(this.compute_all(product_taxes, base)).flatten();

            _(all_taxes).each(function (tax) {
                if (tax.price_include) {
                    totalNoTax -= tax.amount;
                } else {
                    totalTax += tax.amount;
                }
                taxtotal += tax.amount;
                taxdetail[tax.id] = tax.amount;
            });
            totalNoTax = round_pr(totalNoTax, this.pos.currency.rounding);

            return {
                "priceWithTax": totalTax,
                "priceWithoutTax": totalNoTax,
                "tax": taxtotal,
                "taxDetails": taxdetail,
            };
        },
        set_discount: function (discount, actionType, arguments) {
            var disc = discount;
            this.discount = disc;
            if (actionType == 'prod_disc_fix' || actionType == 'cat_disc_fix' || actionType == 'prod_sub_disc_fix') {
                this.discountStr = 'fixed amount: ' + arguments + '';

            } else if (actionType == 'prod_disc_perc' || actionType == 'cat_disc_perc' || actionType == 'prod_sub_disc_perc') {
                this.discountStr = ': ' + arguments + '%';

            }

            this.trigger('change', this);
        },

        get_discount: function () {
            return this.discount;
        },
        can_be_merged_with: function (orderline) {

            if (this.get_product().id !== orderline.get_product().id) {    //only orderline of the same product can be merged
                return false;

            } else if (this.get_product_type() !== orderline.get_product_type()) {
                return false;

            } else if (this.price !== orderline.price) {
                return false;
            } else {
                return true;
            }
        },
        merge: function (orderline, actionType, arguments) {
            this.set_quantity(this.get_quantity() + orderline.get_quantity());

            var discount = orderline.get_discount();

            if (actionType == 'prod_disc_fix' || actionType == 'prod_disc_perc' || actionType == 'cat_disc_fix' || actionType == 'cat_disc_perc') {
                this.set_discount(discount, actionType, arguments);
            }
            else if (actionType == 'prod_sub_disc_perc' || actionType == 'prod_sub_disc_fix') {
                //this.set_discount(orderline.discount, actionType, arguments);
                this.set_discount(discount, actionType, arguments);
            }

        },
        customMerge: function (actionType, discountPrice, arguments) {

            var posOrder = this.pos.get('selectedOrder');
            var discount = discountPrice;

            if (actionType == 'prod_disc_fix' || actionType == 'cat_disc_fix') {
                this.set_discount(discount, actionType, arguments);
            } else if (actionType == 'prod_disc_perc' || actionType == 'cat_disc_perc') {
                this.set_discount(discount, actionType, arguments);
            }
            else if (actionType == 'prod_sub_disc_perc' || actionType == 'prod_sub_disc_fix') {
                //this.set_discount(orderline.discount, actionType, arguments);
                this.set_discount(discount, actionType, arguments);
            } else if (actionType == 'cart_disc_perc' || actionType == 'cart_disc_perc' || actionType == 'cart_disc_fix_perc' || actionType == 'cart_disc_fix_perc') {
                posOrder.setDiscountAmount(discount);
            }
        }


    });

    module.Order = module.Order.extend({

        initialize: function (attributes) {
            Backbone.Model.prototype.initialize.apply(this, arguments);
            this.pos = attributes.pos;
            this.sequence_number = this.pos.pos_session.sequence_number++;
            this.uid = this.generateUniqueId();
            this.set({
                creationDate: new Date(),
                orderLines: new module.OrderlineCollection(),
                paymentLines: new module.PaymentlineCollection(),
                name: _t("Order ") + this.uid,
                client: null,
            });
            this.selected_orderline = undefined;
            this.selected_paymentline = undefined;
            this.screen_data = {};  // see ScreenSelector
            this.receipt_type = 'receipt';  // 'receipt' || 'invoice'
            this.temporary = attributes.temporary || false;
            this.discountAmounts = 0;

            return this;
        },
        getOrderline: function (id) {
            var orderlines = this.get('orderLines').models;
            for (var i = 0; i < orderlines.length; i++) {
                if (orderlines[i].id === id) {
                    return orderlines[i];
                }
            }
            return null;
        },
        setDiscountAmount: function (discountAmounts) {
            this.discountAmounts = discountAmounts;
            //this.trigger('change',this);
        },
        getDiscountAmount: function () {
            return this.discountAmounts;
        },

        getDisTotal: function () {
            return this.getSubtotal() > 0 ? (this.getSubtotal() - this.discountAmounts) : 0;
        },
        getSubtotal: function () {
            return round_pr((this.get('orderLines')).reduce((function (sum, orderLine) {
                return sum + orderLine.get_display_price();
            }), 0), this.pos.currency.rounding);
        },

        addProduct: function (product, prodDiscPrice, actionType, arguments, promosRulesActions, options) {
            if (this._printed) {
                this.destroy();
                return this.pos.get('selectedOrder').addProduct(product);
            }
            options = options || {};
            var attr = JSON.parse(JSON.stringify(product));
            attr.pos = this.pos;
            attr.order = this;
            var line = new module.Orderline({}, {pos: this.pos, order: this, product: product});

            if (options.quantity !== undefined) {
                line.set_quantity(options.quantity);
            }
            if (options.price !== undefined) {
                line.set_unit_price(options.price);
            }
            if (options.discount !== undefined) {
                line.set_discount(options.discount);
            }

            var last_orderline = this.getLastOrderline();
            if (actionType !== undefined) {

                if (actionType == 'cart_disc_perc' || actionType == 'cart_disc_fix') {
                    var posOrder = this.pos.get('selectedOrder');
                    posOrder.setDiscountAmount(prodDiscPrice);

                }
                if (actionType !== 'prod_sub_disc_perc' || actionType !== 'prod_sub_disc_fix') {
                    line.set_discount(prodDiscPrice, actionType, arguments);

                }

                if (actionType == 'cat_disc_perc' || actionType == 'cat_disc_fix') {

                    line.set_discount(prodDiscPrice, actionType, arguments);
                }

            }
            if (last_orderline && last_orderline.can_be_merged_with(line) && options.merge !== false) {
                last_orderline.merge(line, actionType, arguments);
            } else {
                this.get('orderLines').add(line);
            }
            this.selectLine(this.getLastOrderline());


        },
        getCustomTotalTaxIncluded: function () {
            return this.getTotalTaxExcluded() + this.getTax();

        },
        getCustomSubtotal: function () {

            var disCountTotal = this.getDiscountAmount();
            //var disCountTotal = this.get_discount();

            var promosRulesAction = this.pos.promos_rules_actions;
            var promosRulesActions = promosRulesAction[0];
            if (promosRulesActions !== undefined) {


                if (promosRulesActions.action_type == 'cart_disc_perc' || promosRulesActions.action_type == 'prod_disc_perc') {
                    return this.getSubtotal() - disCountTotal;
                    //return this.getSubtotal();

                }
                else if (promosRulesActions.action_type == 'cart_disc_fix') {
                    return this.getSubtotal() - disCountTotal;
                    // return this.getSubtotal();
                }

                else if (promosRulesActions.action_type == 'prod_sub_disc_perc') {
                    return this.getSubtotal() - disCountTotal;
                    //return this.getSubtotal();
                }
                else if (promosRulesActions.action_type == 'prod_sub_disc_fix') {
                    return this.getSubtotal() - disCountTotal;
                }
            }

            return this.getSubtotal();


        },
        getTotalTaxIncluded: function () {
            return this.getCustomSubtotal();
            //return this.getTotalTaxExcluded() + this.getTax();
        },
        getChange: function () {

            return this.getPaidTotal() - this.getTotalWithTax();
        },
        getTotalWithTax: function () {
            var currentOrder = this.pos.get('selectedOrder');

            var promosRulesActions = currentOrder.get('pos').promos_rules_actions;
            var promosRuleAction = {};
            var taxes = 0;
            var totalWithDiscount = 0;
            var totalWithTax = 0;
            for (var m = 0, mLen = promosRulesActions.length; m < mLen; m++) {

                taxes = currentOrder.getTax();
                totalWithDiscount = currentOrder.getDisTotal();
                totalWithTax = totalWithDiscount + taxes;

                return totalWithTax.toFixed(2);


            }


            return totalWithTax.toFixed(2);
        },

        getDueTotal: function () {
            return this.getTotalWithTax() - this.getPaidTotal();
        },

        export_as_JSON: function () {
            var orderLines, paymentLines;
            orderLines = [];
            (this.get('orderLines')).each(_.bind(function (item) {
                return orderLines.push([0, 0, item.export_as_JSON()]);
            }, this));
            paymentLines = [];
            (this.get('paymentLines')).each(_.bind(function (item) {
                return paymentLines.push([0, 0, item.export_as_JSON()]);
            }, this));
            return {
                name: this.getName(),
                amount_paid: this.getPaidTotal(),
                amount_total: this.getTotalWithTax(),
                amount_tax: this.getTax(),
                amount_return: this.getChange(),
                lines: orderLines,
                statement_ids: paymentLines,
                pos_session_id: this.pos.pos_session.id,
                partner_id: this.get_client() ? this.get_client().id : false,
                user_id: this.pos.cashier ? this.pos.cashier.id : this.pos.user.id,
                uid: this.uid,
                sequence_number: this.sequence_number,
                total_order_amount: this.getDisTotal(),
                cal_discount_amount: this.getDiscountAmount(),
                //discount_type: 'percent',
                // percent_discount: 10,
            };
        },
        currentSubtotal: function (posOrder, product, cart_quantity) {
            var selectedOrderLine = this.pos.get('selectedOrder').selected_orderline;
            var prevSubTotal = 0;
            var currentSubTotal = 0;
            var storeSubTotal = 0;

            if (selectedOrderLine != undefined) {

                var selectedQty = selectedOrderLine.quantity;
                var selectedPrice = selectedOrderLine.price;
                var selectedTotalPrice = (selectedQty * selectedPrice);

                if (product.id != posOrder.selected_orderline.product.id) {
                    prevSubTotal = posOrder.getSubtotal();
                    currentSubTotal = (product.price) + (prevSubTotal);

                } else {
                    prevSubTotal = posOrder.getSubtotal();
                    currentSubTotal = (cart_quantity * product.price) + (prevSubTotal - selectedTotalPrice);
                }

            }
            else {
                currentSubTotal = product.price;
                storeSubTotal = currentSubTotal;
            }

            return currentSubTotal;
        },

        /*
         -Loop through the promosRuless
         -Check promotion is active or not
         -Clear existing promotion line
         -evaluate(promtion_rule, order)
         -after evaluation
         -execute_action(promos_id, order_id)
         */
        applyPromotionLine: function (posOrder, product, quantityFlag, cart_quantity) {

            var self = this;
            var executeAction = {};
            var category = self.pos.db.get_category_by_id(product.pos_categ_id[0]);
            var cartQuantity = 1;


            var promosRuleConditionExp = {};
            var result = false;
            var promosRulesConditionsExp = posOrder.get('pos').promos_rules_conditions_exps;
            //var promosLen = promosRulesConditionsExp.length;

            for (var m = 0, promosLen = promosRulesConditionsExp.length; m < promosLen; m++) {
                promosRuleConditionExp = promosRulesConditionsExp[m];
                // stop checking rule if stop-further is true
                if (promosRuleConditionExp.stop_further !== true) {

                    var isFalse = promosRuleConditionExp.value;

                    var orderLine = posOrder.getSelectedLine();
                    //var selectedPrice = orderLine.price;
                    // var cart_quantity = 1;
                    var splitArray = [];

                    if (isFalse == false) {
                        if (orderLine == undefined) {
                            cartQuantity = 1;

                        } else if (product.id == orderLine.product.id) {
                            if (quantityFlag !== true) {
                                cartQuantity = orderLine.quantity + 1;

                            } else {
                                cartQuantity = cart_quantity;
                            }
                        } else {
                            cartQuantity = 1;

                        }
                        result = self.evaluateLine(posOrder, product, cartQuantity, promosRuleConditionExp, product.price);
                        if (result == false) {
                            continue;
                        } else {
                            result = true;
                            break;
                        }
                    } else {
                        var promosExpCodeSplit = promosRuleConditionExp.value.split(',');
                        var count = 0;
                        for (var i = 0, proLen = promosExpCodeSplit.length; proLen > i; i++) {
                            if ((orderLine == undefined && category.code == promosExpCodeSplit[i]) || (orderLine == undefined && product.default_code == promosExpCodeSplit[i])) {
                                splitArray.push(promosExpCodeSplit[i]);
                                cartQuantity = 1;
                                break;

                            } else if ((orderLine != undefined && category.code == promosExpCodeSplit[i] && product.id == orderLine.product.id) || (orderLine != undefined && product.default_code == promosExpCodeSplit[i] && product.id == orderLine.product.id)) {
                                if (quantityFlag !== true) {
                                    splitArray.push(promosExpCodeSplit[i]);
                                    cartQuantity = orderLine.quantity + 1;
                                    break;

                                } else {
                                    splitArray.push(promosExpCodeSplit[i]);
                                    cartQuantity = cart_quantity;
                                    break;
                                }

                            } else if ((orderLine != undefined && category.code == promosExpCodeSplit[i] && product.id !== orderLine.product.id) || (orderLine != undefined && product.default_code == promosExpCodeSplit[i] && product.id != orderLine.product.id)) {
                                if (count == 0) {
                                    splitArray.push(promosExpCodeSplit[i]);
                                    cartQuantity = 1;
                                    count = count + 1;
                                    break;

                                } else {
                                    if (quantityFlag !== true) {
                                        splitArray.push(promosExpCodeSplit[i]);
                                        cartQuantity = orderLine.quantity + 1;
                                        break;

                                    } else {
                                        splitArray.push(promosExpCodeSplit[i]);
                                        cartQuantity = cart_quantity;
                                        break;

                                    }


                                }
                            }
                        }
                        result = self.evaluateLine(posOrder, product, cartQuantity, promosRuleConditionExp, splitArray[0]);
                        if (result == false) {
                            continue;
                        } else {
                            result = true;
                            break;
                        }
                    }
                }//
                //var result = self.evaluateLine(promosRule, posOrder, product, cart_quantity);
            }
            if (result) {
                try {
                    //Execute the action here
                    executeAction = self.executeActionsLine(posOrder, product, cartQuantity, category)
                    return executeAction;
                } catch (error) {
                    //TODO:
                }

            }


            //var result = self.evaluateLine(promosRule, posOrder, product, cart_quantity, promosRulesActionObject);

            return executeAction;

        },
        /*
         evaluate if the promotion is valid
         sales.py: evaluate_line()
         */
        evaluateLine: function (posOrder, product, cart_quantity, promosRuleExp, splitArray) {

            var self = this;


            var result = 'Execution Failed';
            try {
                result = self.expressionEvaluateLine(promosRuleExp, posOrder, product, cart_quantity, splitArray);
                return result;

            } catch (error) {
                return false;
            }

            return false;
        },

        checkPrimaryConditionsLine: function (promosRule, posOrder) {
            var self = this;
            /*
             check Date
             Check if the customer is in the specified partner cats
             -get all the partners
             - check with partner.id = partner_cat.id
             */
            var partners = posOrder.get_client();
            var partnerCategorys = promosRule.partner_categories;

            //check the date with present date
            var fromDate = promosRule.from_date;
            var toDate = promosRule.to_date;
            var date = new Date();
            var day = date.getDate();
            var month = date.getMonth() + 1;
            var year = date.getFullYear();
            var today = year + '-' + month + '-' + day;
            /*
             -if promotion date is applicable
             -if partner is applicable for the promotion
             -if conditon is matched
             then retun 'True'
             or return 'False'
             */
            if (self.promotionLineDate(fromDate) <= self.promotionLineDate(toDate)) {
                if (self.promotionLineDate(fromDate) <= self.promotionLineDate(toDate)) {
                    if (self.promotionLineDate(today) >= self.promotionLineDate(fromDate)) {
                        if (partners != null && partnerCategorys.length > 0) {// promotion apply for particular user
                            for (var i = 0, len = partnerCategorys.length; i < len; i++) {
                                if (partners.category_id[0] == partnerCategorys[i]) {
                                    return true;
                                }
                            }
                        } else if (partnerCategorys.length == 0) {//promotion apply for every if user is not set
                            return true;
                        } else {
                            return false;
                        }
                    } else {
                        return false;
                    }

                }
            } else {
                return false;
            }


        },
        /*
         -Evaluate the expression in a given environment
         */
        expressionEvaluateLine: function (promosRuleExp, posOrder, product, cart_quantity, splitArray) {
            var self = this;
            // var promosRuleExp = posOrder.get('pos').promos_rules_conditions_exps;


            var promosRuleExpAttribute = promosRuleExp.attribute;
            var ruleTrue = true;
            var ruleFalse = false;
            var exp = promosRuleExp;

            var comparator = exp.comparator;
            var category = self.pos.db.get_category_by_id(product.pos_categ_id[0]);
            if (promosRuleExpAttribute == 'prod_qty') {

                if (product !== undefined && category !== undefined) {

                    if ((product.default_code !== undefined && splitArray == product.default_code) || (category.code !== undefined && splitArray == category.code )) {

                        if (comparator == '==' && cart_quantity == exp.quantity) {
                            return ruleTrue;
                        }
                        else if (comparator == '>=' && cart_quantity >= exp.quantity) {
                            return ruleTrue;
                        }
                        else if (comparator == '!=' && cart_quantity != exp.quantity) {
                            return ruleTrue;
                        }
                        else if (comparator == '>' && cart_quantity > exp.quantity) {
                            return ruleTrue;
                        }
                        else {
                            return ruleFalse;
                        }
                    }
                }

            } else if (promosRuleExpAttribute == 'amount_total' || promosRuleExpAttribute == 'amount_include_total') {// promotion will be on total amount
                var currentSubTotal = 0;
                var expValue = exp.price;

                if (promosRuleExpAttribute == 'amount_total') {
                    currentSubTotal = this.currentSubtotal(posOrder, product, cart_quantity);

                } else {
                     var productTaxes = this.pos.taxes;

                    var taxAmount = 0;
                    for(var m = 0, len = productTaxes.length; m < len; m++){
                        if(product.taxes_id[0] == productTaxes[m].id){
                            taxAmount = productTaxes[m].amount;

                        }
                    }
                    /*
                        productTax -> for calculating 1st product tax
                        tax -> it will be the selected orderLine tax
                     */
                    var productTax = product.price * taxAmount;
                    var totalIncludedTax = this.currentSubtotal(posOrder, product, cart_quantity);
                    var tax = posOrder.getTax();
                    currentSubTotal = totalIncludedTax + tax + productTax;

                }

                if (currentSubTotal >= expValue) {
                    if ((comparator == '==' && currentSubTotal == expValue)) {
                        return ruleTrue;
                    }
                    else if ((comparator == '>=' && currentSubTotal >= expValue)) {
                        return ruleTrue;
                    }

                    else if ((comparator == '!=' && currentSubTotal != expValue)) {
                        return ruleTrue;
                    }
                    else if ((comparator == '>' && currentSubTotal > expValue)) {
                        return ruleTrue;
                    }

                    else {
                        return ruleFalse;
                    }
                }
            } else if (promosRuleExpAttribute == 'prod_unit_price') { // same category but product.price>500
                if (product !== undefined && category !== undefined) {

                    if ((product.default_code !== undefined && splitArray == product.default_code) || (category.code !== undefined && splitArray == category.code )) {

                        if (comparator == '==' && cart_quantity == exp.quantity && product.price == exp.price) {
                            return ruleTrue;
                        }
                        else if (comparator == '>=' && cart_quantity >= exp.quantity && product.price >= exp.price) {
                            return ruleTrue;
                        }

                        else if (comparator == '!=' && cart_quantity != exp.quantity && product.price != exp.price) {
                            return ruleTrue;
                        }
                        else if (comparator == '>' && cart_quantity > exp.quantity && product.price > exp.price) {
                            return ruleTrue;
                        }
                        else {
                            return ruleFalse;
                        }
                    }
                }
            }
            return ruleFalse;

        },

        executeActionsLine: function (posOrder, product, cart_quantity, category) {
            var self = this;
            var discountObject = {};
            var promosRulesActions = posOrder.get('pos').promos_rules_actions;
            var promosRuleAction = {};
            for (var m = 0, mLen = promosRulesActions.length; m < mLen; m++) {
                promosRuleAction = promosRulesActions[m];


                var methodPrefix = 'action_';
                var method = '';
                if (promosRuleAction.product_code == false) {
                    method = promosRuleAction.action_type;
                    discountObject = self[methodPrefix + method](promosRuleAction, posOrder, product, cart_quantity);

                    return discountObject;
                }
                else if (promosRuleAction.product_code !== false) {
                    var promosActionCodeSplit = promosRuleAction.product_code.split(',');

                    for (var n = 0, nLen = promosActionCodeSplit.length; n < nLen; n++) {
                        if ((promosActionCodeSplit[n] == product.default_code) || (promosActionCodeSplit[n] == category.code)) {
                            method = promosRuleAction.action_type;
                            discountObject = self[methodPrefix + method](promosRuleAction, product, cart_quantity);

                            return discountObject;
                        }
                    }
                }


            }
            return discountObject;
        },
        promotionLineDate: function (strDate) {
            //TODO: conversion on date('%Y-%m-%d %H:%M:%S' or '%Y-%m-%d')
            var parts = strDate.split("-");

            return new Date(parts[0], parts[1] - 1, parts[2]);
        },
        action_prod_disc_perc: function (promosRuleAction, product, cart_quantity) {

            var discountObject = {};
            discountObject = this.discountCalculationPerc(promosRuleAction, product, cart_quantity);

            return discountObject;
        },
        action_prod_disc_fix: function (promosRuleAction, product, cart_quantity) {

            var discountObject = {};
            discountObject = this.discountCalculationFix(promosRuleAction, product, cart_quantity);

            return discountObject;
        },
        action_prod_sub_disc_perc: function (promosRuleAction, product, cart_quantity) {

            var discountObject = {};
            discountObject = this.discountCalculationPerc(promosRuleAction, product, cart_quantity);

            return discountObject;
        },
        action_prod_sub_disc_fix: function (promosRuleAction, product, cart_quantity) {

            var discountObject = {};
            discountObject = this.discountCalculationSubFix(promosRuleAction, product, cart_quantity);

            return discountObject;
        },
        action_cat_disc_perc: function (promosRuleAction, product, cart_quantity) {

            var discountObject = {};
            discountObject = this.discountCalculationPerc(promosRuleAction, product, cart_quantity);

            return discountObject;
        },

        action_cat_disc_fix: function (promosRuleAction, product, cart_quantity) {

            var discountObject = {};
            discountObject = this.discountCalculationFix(promosRuleAction, product, cart_quantity);

            return discountObject;
        },
        /*
         -discount on subtotal with out tax
         */
        action_cart_disc_fix: function (promosRulesAction, posOrder, product) {
            var subTotal = posOrder.getSubtotal();
            var discountObject = {};
            var discountAmount = 0;

            try {
                if (subTotal == 0) {
                    subTotal = product.price;
                }
                discountAmount = promosRulesAction.arguments;
                discountObject['action_type'] = promosRulesAction.action_type;
                discountObject['arguments'] = promosRulesAction.arguments;
                discountObject['discountPrice'] = discountAmount;
                return discountObject;
            } catch (error) {
                alert('action_cart_disc_fixed' + ' method error ');

            }

        },
        action_cart_disc_perc: function (promosRulesAction, posOrder, product, cart_quantity) {
            var subTotal = posOrder.getSubtotal();
            var discountObject = {};
            var discountAmount = 0;

            var currentSubTotal = this.currentSubtotal(posOrder, product, cart_quantity);
            try {
                if (subTotal == 0) {
                    subTotal = product.price;
                    discountAmount = (subTotal) * (promosRulesAction.arguments / 100);
                } else {
                    discountAmount = currentSubTotal * (promosRulesAction.arguments / 100);
                }
                //var arguments = promosRulesAction.arguments;
                discountObject['action_type'] = promosRulesAction.action_type;
                discountObject['arguments'] = promosRulesAction.arguments;
                discountObject['discountPrice'] = discountAmount;
                return discountObject;
            } catch (error) {
                alert('action_cart_disc_perc' + ' method error ');
            }
            return discountObject;
        },


        discountCalculationFix: function (promosRuleAction, product, cart_quantity) {
            var self = this;
            var discountCalculation = {};

            var productCategory = self.pos.db.get_category_by_id(product.pos_categ_id[0]);
            var discountPrice = 0;

            discountPrice = (cart_quantity * promosRuleAction.arguments);
            discountCalculation['action_type'] = promosRuleAction.action_type;
            discountCalculation['arguments'] = promosRuleAction.arguments;
            discountCalculation['discountPrice'] = discountPrice;

            return discountCalculation;
        },
        discountCalculationSubFix: function (promosRuleAction, product, cart_quantity) {
            var self = this;
            var discountCalculation = {};

            var productCategory = self.pos.db.get_category_by_id(product.pos_categ_id[0]);
            var discountPrice = 0;

            discountPrice = promosRuleAction.arguments;
            discountCalculation['action_type'] = promosRuleAction.action_type;
            discountCalculation['arguments'] = promosRuleAction.arguments;
            discountCalculation['discountPrice'] = discountPrice;

            return discountCalculation;
        },
        discountCalculationPerc: function (promosRuleAction, product, cart_quantity) {
            var self = this;
            var discountCalculation = {};

            var productCategory = self.pos.db.get_category_by_id(product.pos_categ_id[0]);
            var discountPrice = 0;

            discountPrice = (cart_quantity * product.price ) * (promosRuleAction.arguments / 100);
            discountCalculation['action_type'] = promosRuleAction.action_type;
            discountCalculation['arguments'] = promosRuleAction.arguments;
            discountCalculation['discountPrice'] = discountPrice;

            return discountCalculation;

        },


        ///

        getPoint: function () {
            var client = this.get('client');
            return client ? client.point_loyalty : "";
        },

        get_client_address: function () {
            var client = this.get('client');
            return client ? client.address : "";
        },
        get_client_phone: function () {
            var client = this.get('client');
            return client ? client.phone : "";
        },
        get_client_email: function () {
            var client = this.get('client');
            return client ? client.email : "";
        },
        get_custom_amount_to_text: function () {
            var currentorder = this.pos.get('selectedOrder');
            //var totalamount = currentorder.getTotalTaxIncluded();
            var totalAmount = currentorder.getTotalWithTax();
            var amount = this.amount_to_words(totalAmount);

            return amount;
        },

        // ////
        get_client_name: function () {
            var client = this.get('client');
            $('.loyl_entry').text("Total Point:" + client.point_loyalty);
            return client ? client.name : "";
        },
        getRedemPoint: function () {
            return this.getPoint();
        },
        getRedemLeft: function () {
            if (this.getRedemPoint() >= this.getDueLeft()) {
                return this.getDueLeft();
            } else if (this.getRedemPoint() < this.getDueLeft()) {
                return this.getRedemPoint();
            } else {
                return 0;
            }

        },
        getRewardLeft: function () {
            if (this.getRewardPoint() >= this.getDueLeft()) {
                return this.getDueLeft();
            } else if (this.getRewardPoint() < this.getDueLeft()) {
                return this.getRewardPoint();
            } else {
                return 0;
            }
        },
        getRedemTotal: function () {
            var self = this;
            return round_pr((this.get('paymentLines')).reduce((function (sum,
                                                                         paymentLine) {
                if (paymentLine.is_redemption == true) {
                    return sum + paymentLine.get_amount();
                } else {
                    return sum;
                }
            }), 0), this.pos.currency.rounding);
        },
        getRedemptionRule: function () {

            var self = this;
            var redemRules = [];
            var redemptionRules = this.get('pos').redemption_rules;
            for (i = 0, len = redemptionRules.length; i < len; i++) {
                var redemRule = redemptionRules[i];
                if (redemRule.is_active == true) {
                    redemRules.push(redemRule);
                }
            }
            return redemRules[0];
        },
        /*
            -rewardPoint calculation
            - default value is 1
         */

        getRewardPoint: function () {

            var redemRule = this.getRedemptionRule();
            if (redemRule !== undefined) {

                var loyaltyPoint = this.getRedemPoint();
                var rewordPoint = 0;
                var DEFAULT_UNIT = 1;
                var pointStartMargin = redemRule.point_start_margin;
                var pointEndMargin = redemRule.point_end_margin;
                var rewardPointUnit = redemRule.reward_point_unit;
                if (loyaltyPoint >= pointStartMargin
                    && loyaltyPoint <= pointEndMargin) {
                    rewordPoint = loyaltyPoint * rewardPointUnit;
                    return rewordPoint.toFixed(2);
                } else {
                    rewordPoint = loyaltyPoint * DEFAULT_UNIT;
                    return rewordPoint.toFixed(2);
                }

            } else {
                return;
            }


        },
        getRewardToLoyaltyPoint: function () {
            var client = this.get('client');
            var redemRule = this.getRedemptionRule();
            if (client != null && redemRule !== undefined) {
                var rewardPoint = this.getRewardPoint();

                var redemTotal = this.getRedemTotal().toFixed(2);
                var rewardChange = rewardPoint - redemTotal;
                var rewardPointUnit = redemRule.reward_point_unit;
                var loyaltyPoint = rewardPoint / rewardPointUnit;

                if (rewardChange > 0) {
                    var loyaltyPoint = rewardChange / rewardPointUnit;
                    return loyaltyPoint;
                } else {
                    return 0;
                }
            } else if (redemRule == undefined) {
                alert('need to defined redemption rule');
            } else {
                return 0;
            }
        },

        addPaymentline: function (cashregister) {
            var paymentLines = this.get('paymentLines');
            var newPaymentline = new module.Paymentline({}, {
                cashregister: cashregister,
                pos: this.pos
            });
            var currentOrder = {};

            if (cashregister.journal.type == 'cash'
                && cashregister.journal.is_redemption == true) {
                var clientInfo = this.get_client();
                if (clientInfo != null) {
                    currentOrder = this.pos.get('selectedOrder');

                    var rewardPoint = currentOrder.getRewardPoint();
                    //var redemPoint = currentOrder.getRewardToLoyaltyPoint();
                    var redemTotal = currentOrder.getRedemTotal();
                    var paidTotal = currentOrder.getPaidTotal();
                    var rewardChange = rewardPoint - redemTotal;
                    var dueTotal = currentOrder.getTotalWithTax();
                    var remaining = dueTotal > paidTotal ? dueTotal - paidTotal
                        : 0;
                    if (rewardChange >= remaining) {
                        newPaymentline.set_amount(remaining);
                    } else {
                        newPaymentline.set_amount(rewardChange);
                    }
                }
            }
            else if (cashregister.journal.type !== 'cash') {
                newPaymentline.set_amount(Math.max(this.getDueTotal(), 0));
            }
            paymentLines.add(newPaymentline);
            this.selectPaymentline(newPaymentline);
        },
    });

    module.ProductListWidget.include({
        init: function (parent, options) {
            var self = this;
            this._super(parent, options);
            this.model = options.model;
            this.productwidgets = [];
            this.weight = options.weight || 0;
            this.show_scale = options.show_scale || false;
            this.next_screen = options.next_screen || false;

            this.click_product_handler = function (event) {
                var product = self.pos.db.get_product_by_id(this.dataset['productId']);
                var posOrder = self.pos.get('selectedOrder');

                var promosRules = posOrder.get('pos').promotion_rules;
                var promosRule = promosRules[0];


                var actionType = "";
                var arguments = "";
                var prodDiscPrice = "";
                //var promosRulesActions = {};
                //check primary condition here


                if (promosRule !== undefined && promosRule.active == true) {
                    var primaryCondition = posOrder.checkPrimaryConditionsLine(promosRule, posOrder);
                    if (primaryCondition) {
                        try {
                            var posProductObject = {};
                            var quantityFlag = false;
                            posProductObject = posOrder.applyPromotionLine(posOrder, product, quantityFlag);

                            if (posProductObject !== undefined || posProductObject !== '') {
                                prodDiscPrice = posProductObject.discountPrice;
                                arguments = posProductObject.arguments;
                                product['discPrice'] = posProductObject.discountPrice;
                                product['discType'] = posProductObject.action_type;
                                product['arguments'] = posProductObject.arguments;
                                actionType = product['discType'];
                            }

                        } catch (error) {
                            console.log(error);
                        }

                    }


                }
                options.click_product_action(product, prodDiscPrice, actionType, arguments);
            };

            this.product_list = options.product_list || [];
            this.product_cache = new module.DomCache();
        },
        ///***** start//
    });
    module.OrderWidget.include({

        set_value: function (val) {
            var cart_quantity = val;
            //var product = this.pos.db.get_product_by_id(this.dataset['productId']);

            var posOrder = this.pos.get('selectedOrder');
            var orderLine = posOrder.selected_orderline;
            if (this.editable && posOrder.getSelectedLine() && cart_quantity != '') {
                var product = orderLine.product;
                var mode = this.numpad_state.get('mode');//posOrder, product
                if (mode === 'quantity') {
                    var quantityFlag = true;
                    var promotionObject = posOrder.applyPromotionLine(posOrder, product, quantityFlag, cart_quantity);

                    var actionType = promotionObject.action_type;
                    var arguments = promotionObject.arguments;
                    var discountPrice = promotionObject.discountPrice;
                    orderLine.customMerge(actionType, discountPrice, arguments);
                    posOrder.getSelectedLine().set_quantity(val);
                } else if (mode === 'price') {
                    posOrder.getSelectedLine().set_unit_price(val);
                }
            }
        },

        update_summary: function () {
            var order = this.pos.get('selectedOrder');
            var promosRulesActions = order.get('pos').promos_rules_actions;
            if (promosRulesActions !== undefined && promosRulesActions.length > 0) {
                //var total = order ? order.getCustomTotalTaxIncluded() : 0;
                //var taxes = order ? total - order.getTotalTaxExcluded() : 0;
                var taxes = 0;
                var totalWithDiscount = 0;
                var total = 0;
                var totalDiscount = 0;

                for (var n = 0, len = promosRulesActions.length; len > n; n++) {
                    var method = promosRulesActions[n].action_type;
                    var arguments = promosRulesActions[n].arguments;


                    if (method == 'prod_disc_perc' || method == 'prod_disc_fix' || method == 'cat_disc_perc' || method == 'cat_disc_fix' || method == 'prod_sub_disc_perc' || method == 'prod_sub_disc_fix') {

                        taxes = order.getTax();
                        totalWithDiscount = order.getDisTotal();
                        total = totalWithDiscount + taxes;
                        totalDiscount = order.getDiscountAmount();

                        this.el.querySelector('.summary .total div > .subtotal').textContent = this.format_currency(totalWithDiscount);
                        this.el.querySelector('.summary .total div > .total_value').textContent = this.format_currency(total);
                        this.el.querySelector('.summary .total .subentry .value').textContent = this.format_currency(taxes);
                    }
                    else if (method == 'cart_disc_perc' || method == 'cart_disc_fix') {
                        taxes = order.getTax();
                        totalWithDiscount = order.getDisTotal();
                        total = totalWithDiscount + taxes;
                        totalDiscount = order.getDiscountAmount();

                        $(".discount_hide_show").css("display", "block");
                        this.el.querySelector('.summary .total div > .subtotal').textContent = this.format_currency(totalWithDiscount);
                        this.el.querySelector('.summary .total div > .discount_value').textContent = this.format_currency(totalDiscount);
                        this.el.querySelector('.summary .total div > .total_value').textContent = this.format_currency(total);
                        this.el.querySelector('.summary .total .subentry .value').textContent = this.format_currency(taxes);
                    }

                }
            }
        },

    });

    module.ProductScreenWidget.include({
        start: function () { //FIXME this should work as renderElement... but then the categories aren't properly set. explore why
            var self = this;

            this.product_list_widget = new module.ProductListWidget(this, {
                click_product_action: function (product, prodDiscPrice, actionType, arguments, promosRulesActions) {
                    if (product.to_weight && self.pos.config.iface_electronic_scale) {
                        self.pos_widget.screen_selector.set_current_screen('scale', {product: product});
                    } else {
                        self.pos.get('selectedOrder').addProduct(product, prodDiscPrice, actionType, arguments, promosRulesActions);
                    }
                },
                product_list: this.pos.db.get_product_by_category(0)
            });
            this.product_list_widget.replace(this.$('.placeholder-ProductListWidget'));

            this.product_categories_widget = new module.ProductCategoriesWidget(this, {
                product_list_widget: this.product_list_widget,
            });
            this.product_categories_widget.replace(this.$('.placeholder-ProductCategoriesWidget'));
        },
    });



    module.ClientListScreenWidget = module.ClientListScreenWidget
        .extend({
            update_point_from_order: function (partner) {
                var self = this;
                var pointUpdate = [{
                    id: partner.id,
                    point_loyalty: partner.point_loyalty
                }];
                new instance.web.Model('res.partner')
                    .call('create_from_ui', pointUpdate)
                    .then(
                        function (partner_id) {
                            console
                                .log(" successfully update point to res_partner "
                                    + partner_id);
                        },
                        function (err, event) {
                            event.preventDefault();
                            self.pos_widget.screen_selector
                                .show_popup(
                                    'error',
                                    {
                                        'message': _t('Error: Could not Save Changes'),
                                        'comment': _t('Your Internet connection is probably down.'),
                                    });
                        });
            },
        });

    module.PaymentScreenWidget = module.PaymentScreenWidget
        .extend({

            init: function (parent, options) {
                var self = this;
                this._super(parent, options);

                this.pos.bind('change:selectedOrder', function () {
                    this.bind_events();
                    this.renderElement();
                }, this);

                this.bind_events();
                this.decimal_point = instance.web._t.database.parameters.decimal_point;

                this.line_delete_handler = function (event) {
                    var node = this;
                    while (node && !node.classList.contains('paymentline')) {
                        node = node.parentNode;
                    }
                    if (node) {
                        self.pos.get('selectedOrder').removePaymentline(
                            node.line)
                    }
                    event.stopPropagation();
                };

                this.line_change_handler = function (event) {
                    var node = this;
                    var el = $('input.paymentline-input');
                    var order = self.pos.get('selectedOrder');
                    var journal = order.get('pos').journals;
                    var client = order.get('client');
                    while (node && !node.classList.contains('paymentline')) {
                        node = node.parentNode;
                    }
                    if (node) {
                        var amount;
                        var isValidate = function (value) {
                            var value = this.value
                            if (value < 0) {
                                alert('negetive no');
                            }
                        }
                        try {

                            if (this.value >= 0 && this.value !== '') {
                                amount = instance.web.parse_value(
                                    this.value, {
                                        type: "float"
                                    });
                                node.line.set_amount(amount);
                            } else {

                                var validate = isValidate(this.value);
                                alert('check value');
                                amount = 0;
                                node.line.set_amount(amount);
                            }
                        } catch (e) {
                            amount = 0;
                            node.line.set_amount(amount);
                        }
                    }
                };

                this.line_click_handler = function (event) {
                    var node = this;
                    while (node && !node.classList.contains('paymentline')) {
                        node = node.parentNode;
                    }
                    if (node) {
                        self.pos.get('selectedOrder').selectPaymentline(
                            node.line);
                    }
                };
                this.hotkey_handler = function (event) {
                    if (event.which === 13) {
                        self.validate_order();
                    } else if (event.which === 27) {
                        self.back();
                    }
                };
            },

            update_payment_summary: function () {
                var currentOrder = this.pos.get('selectedOrder');
                var cashRegisters = currentOrder.get('pos').cashregisters;

                var paidTotal = currentOrder.getPaidTotal();
                var dueTotal = currentOrder.getTotalWithTax();
                var remaining = dueTotal > paidTotal ? dueTotal - paidTotal
                    : 0;
                var client = currentOrder.get('client');
                if (client != null || client != '') {
                    var redemptionJournal = [];
                    for (i = 0, len = cashRegisters.length; i < len; i++) {
                        if (cashRegisters[i].journal.is_redemption == true) {
                            var rewardToLoyaltyPoint = currentOrder
                                .getRewardToLoyaltyPoint();
                            var rewardPoint = currentOrder
                                .getRewardPoint();
                            var redemTotal = currentOrder.getRedemTotal();
                            var rewardChange = 0;
                            if (rewardPoint >= redemTotal) {
                                var rewardChange = rewardPoint - redemTotal;

                            } else if (rewardPoint < 0) {

                                return;
                            } else if (redemTotal > rewardPoint) {
                                alert(' point exceed limitations');
                                return;
                            }
                        }
                    }
                }

                var change = paidTotal > dueTotal ? paidTotal - dueTotal
                    : 0;

                var remaining = dueTotal > paidTotal ? dueTotal - paidTotal
                    : 0;
                var change = paidTotal > dueTotal ? paidTotal - dueTotal
                    : 0;

                this.$('.payment-due-total').html(
                    this.format_currency(dueTotal));
                this.$('.payment-paid-total').html(
                    this.format_currency(paidTotal));
                this.$('.payment-remaining').html(
                    this.format_currency(remaining));
                this.$('.payment-change')
                    .html(this.format_currency(change));
                if (rewardChange !== undefined) {
                    this.$('.payment-loyalty-total').html(
                        this.format_currency(rewardChange));
                }

                this.$('.paymentline-input').attr('min', 0);

                if ((client == null || client == '') || ( client != null && redemTotal < 1)) {
                    this.$('.is_redemption').attr('readonly', true);
                }

                if (currentOrder.selected_orderline === undefined) {
                    remaining = 1; // What is this ?
                }

                if (this.pos_widget.action_bar) {
                    this.pos_widget.action_bar.set_button_disabled(
                        'validation', !this.is_paid());
                    this.pos_widget.action_bar.set_button_disabled(
                        'invoice', !this.is_paid());
                }
            },
            is_paid: function () {
                var currentOrder = this.pos.get('selectedOrder');
                var total = currentOrder.getTotalWithTax();
                return (total < 0.000001
                || currentOrder.getPaidTotal() + 0.000001 >= total);

            },
            validate_order: function (options) {
                var self = this;
                options = options || {};

                var currentOrder = this.pos.get('selectedOrder');

                if (currentOrder.get('orderLines').models.length === 0) {
                    this.pos_widget.screen_selector.show_popup('error', {
                        'message': _t('Empty Order'),
                        'comment': _t('There must be at least one product in your order before it can be validated'),
                    });
                    return;
                }

                var plines = currentOrder.get('paymentLines').models;
                for (var i = 0; i < plines.length; i++) {
                    if (plines[i].get_type() === 'bank' && plines[i].get_amount() < 0) {
                        this.pos_widget.screen_selector.show_popup('error', {
                            'message': _t('Negative Bank Payment'),
                            'comment': _t('You cannot have a negative amount in a Bank payment. Use a cash payment method to return money to the customer.'),
                        });
                        return;
                    }
                }

                if (!this.is_paid()) {
                    return;
                }

                // The exact amount must be paid if there is no cash payment method defined.
                if (Math.abs(currentOrder.getTotalWithTax() - currentOrder.getPaidTotal()) > 0.00001) {
                    var cash = false;
                    for (var i = 0; i < this.pos.cashregisters.length; i++) {
                        cash = cash || (this.pos.cashregisters[i].journal.type === 'cash');
                    }
                    if (!cash) {
                        this.pos_widget.screen_selector.show_popup('error', {
                            message: _t('Cannot return change without a cash payment method'),
                            comment: _t('There is no cash payment method available in this point of sale to handle the change.\n\n Please pay the exact amount or add a cash payment method in the point of sale configuration'),
                        });
                        return;
                    }
                }

                if (this.pos.config.iface_cashdrawer) {
                    this.pos.proxy.open_cashbox();
                }

                if (options.invoice) {
                    // deactivate the validation button while we try to send the order
                    this.pos_widget.action_bar.set_button_disabled('validation', true);
                    this.pos_widget.action_bar.set_button_disabled('invoice', true);

                    var invoiced = this.pos.push_and_invoice_order(currentOrder);

                    invoiced.fail(function (error) {
                        if (error === 'error-no-client') {
                            self.pos_widget.screen_selector.show_popup('error', {
                                message: _t('An anonymous order cannot be invoiced'),
                                comment: _t('Please select a client for this order. This can be done by clicking the order tab'),
                            });
                        } else {
                            self.pos_widget.screen_selector.show_popup('error', {
                                message: _t('The order could not be sent'),
                                comment: _t('Check your internet connection and try again.'),
                            });
                        }
                        self.pos_widget.action_bar.set_button_disabled('validation', false);
                        self.pos_widget.action_bar.set_button_disabled('invoice', false);
                    });

                    invoiced.done(function () {
                        self.pos_widget.action_bar.set_button_disabled('validation', false);
                        self.pos_widget.action_bar.set_button_disabled('invoice', false);
                        self.pos.get('selectedOrder').destroy();
                    });

                } else {
                    this.pos.push_order(currentOrder)
                    if (this.pos.config.iface_print_via_proxy) {
                        var receipt = currentOrder.export_for_printing();
                        this.pos.proxy.print_receipt(QWeb.render('XmlReceipt', {
                            receipt: receipt, widget: self,
                        }));
                        this.pos.get('selectedOrder').destroy();    //finish order and go back to scan screen
                    } else {
                        this.pos_widget.screen_selector.set_current_screen(this.next_screen);
                    }
                }

                // hide onscreen (iOS) keyboard
                setTimeout(function () {
                    document.activeElement.blur();
                    $("input").blur();
                }, 250);
            },
        });

};
/*
 * custom js file module need to be
 * added here
 * i.e: openerp_pos_loyalty(instance, module);
 */
openerp.point_of_sale = function (instance) {

    instance.point_of_sale = {};

    var module = instance.point_of_sale;

    openerp_pos_db(instance, module); // import db.js

    openerp_pos_models(instance, module); // import pos_models.js

    openerp_pos_basewidget(instance, module); // import pos_basewidget.js

    openerp_pos_keyboard(instance, module); // import pos_keyboard_widget.js

    openerp_pos_screens(instance, module); // import pos_screens.js

    openerp_pos_devices(instance, module); // import pos_devices.js

    openerp_pos_widgets(instance, module); // import pos_widgets.js

    openerp_pos_promotion_loyalty(instance, module); // import openerp_pos_loyalty.js

    instance.web.client_actions.add('pos.ui',
        'instance.point_of_sale.PosWidget');
};