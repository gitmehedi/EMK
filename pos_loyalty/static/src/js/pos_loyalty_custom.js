function openerp_pos_loyalty(instance, module) { // module is
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

    module.PosModel = Backbone.Model.extend({
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
            this.opunits = [];
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
                    'partner_id', 'country_id', 'street', 'street2', 'zip', 'city',
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
                    'point_loyalty', 'last_purchase_point', 'category_id'],
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
                model: 'operating.unit',
                fields: [],
                domain: function(self){ return [['id','=', self.config.operating_unit_id[0]]]; },
                loaded: function (self, opunit) {
                    self.opunits = opunit[0];
                    self.oppartner = []
                    for (var i = 0; i < opunit[0].length; i++) {
                        if (opunit[i].id === self.company.country_id[0]) {
                            self.company.country = self.opunits.partner_id;
                        }
                    }
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
                            if (startDate <= endDate && startDate !== false && endDate !== false) {
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
                        partner['point_loyalty'] = order.getRewardToLoyaltyPoint();
                        console.log(order.getRewardToLoyaltyPoint())

                    } else {
                        var rewardToLoyaltyPoint = order
                            .getRewardToLoyaltyPoint();
                        var redemTotal = order.getRedemTotal();
                        var dueTotal = order.getTotalTaxIncluded();
                        // var dueTotal = order.getTotalWithTax();

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
    var orderline_id = 1;


    module.Orderline = module.Orderline.extend({
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
        get_price_with_tax: function () {
            return Math.ceil(this.get_all_prices().priceWithTax);
        },
        get_tax: function () {
            return Math.ceil(this.get_all_prices().tax);
        },
        get_unit_price: function(){
            var digits = this.pos.dp['Product Price'];
            // round and truncate to mimic _sybmbol_set behavior
            return Math.ceil(round_di(this.price || 0, digits).toFixed(digits));
        },

    });

    var currentPurchase = 0;

    module.Order = module.Order.extend({
            getPoint: function () {
                var client = this.get('client');
                return client ? client.point_loyalty : 0;
            },
            getCurrentPoint: function () {
                var client = this.get('client');
                if (client) {
                    var todayPoint = this.getPoint() - currentPurchase;
                    return todayPoint;
                } else {
                    return 0;
                }
            },

            get_client_address: function () {
                var client = this.get('client');
                return client ? client.address : "";
            }
            ,
            get_client_phone: function () {
                var client = this.get('client');
                return client ? client.phone : "";
            }
            ,
            get_client_email: function () {
                var client = this.get('client');
                return client ? client.email : "";
            }
            ,
            get_custom_amount_to_text: function () {
                var currentorder = this.pos.get('selectedOrder');
                var totalAmount = currentorder.getTotalTaxIncluded();
                var amount = this.amount_to_words(totalAmount);

                return amount;
            }
            ,
            get_client_name: function () {
                var client = this.get('client');
                if (client) {
                    $('.loyl_entry').text("Total Point:" + client.point_loyalty);
                }
                return client ? client.name : "";
            }
            ,
            getRedemPoint: function () {
                return this.getPoint();
            }
            ,
            getRedemLeft: function () {
                if (this.getRedemPoint() >= this.getDueLeft()) {
                    return this.getDueLeft();
                } else if (this.getRedemPoint() < this.getDueLeft()) {
                    return this.getRedemPoint();
                } else {
                    return 0;
                }

            }
            ,
            getRewardLeft: function () {
                if (this.getRewardPoint() >= this.getDueLeft()) {
                    return this.getDueLeft();
                } else if (this.getRewardPoint() < this.getDueLeft()) {
                    return this.getRewardPoint();
                } else {
                    return 0;
                }
            }
            ,
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
            }
            ,
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
            }
            ,

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


            }
            ,
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
                        currentPurchase = 0;
                        if (currentPurchase == 0) {
                            currentPurchase = loyaltyPoint;
                        }
                        return loyaltyPoint;
                    } else {
                        return 0;
                    }
                } else if (redemRule == undefined) {
                    alert('need to defined redemption rule');
                } else {
                    return 0;
                }
            }
            ,

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

                        var loyaltyRule = currentOrder.get('pos').loyalty_rules;
                        for (var i = 0, len = loyaltyRule.length; i < len; i++) {
                            if (loyaltyRule[i].is_active !== false) {
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

                            } else {
                                console.log('loyalty rule is not active');
                            }

                        }
                    }
                }
                else if (cashregister.journal.type !== 'cash') {
                    newPaymentline.set_amount(Math.max(this.getDueLeft(), 0));
                }
                paymentLines.add(newPaymentline);
                this.selectPaymentline(newPaymentline);
            }
            ,
        }
    )
    ;

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


    module.ClientListScreenWidget = module.ClientListScreenWidget.extend({
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
                        console.log("successfully update point to res_partner " + partner_id);
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

    module.PaymentScreenWidget = module.PaymentScreenWidget.extend({
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
                    var selectedPaymentLine = order.selected_paymentline;

                    var isValidate = function (value) {
                        var value = this.value
                        if (value < 0) {
                            alert('negetive no');
                        } else if (value > order.getRewardToLoyaltyPoint()) {
                            alert('exceed loyalty limit');
                        }
                    }
                    try {
                        if (selectedPaymentLine.is_redemption !== true) {
                            if (this.value >= 0 && this.value !== '') {
                                amount = instance.web.parse_value(this.value, {type: "float"});
                                node.line.set_amount(amount);
                            } else {

                                var validate = isValidate(this.value);
                                //alert('check value');
                                amount = 0;
                                node.line.set_amount(amount);
                            }

                        } else {
                            if (this.value >= 0 && this.value !== '') {
                                amount = instance.web.parse_value(this.value, {type: "float"});
                                if (amount <= order.getRewardToLoyaltyPoint() && order.getRewardToLoyaltyPoint() >= 0) {
                                    node.line.set_amount(amount);
                                } else if (order.getRewardToLoyaltyPoint() > 0 && (amount - order.getRewardToLoyaltyPoint()) <= order.getRewardToLoyaltyPoint()) {
                                    node.line.set_amount(amount);

                                } else {
                                    amount = 0;
                                    node.line.set_amount(amount);
                                }

                            } else {

                                var validate = isValidate(this.value);
                                //alert('check value');
                                amount = 0;
                                node.line.set_amount(amount);
                            }

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
            var dueTotal = currentOrder.getTotalTaxIncluded();
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

            if ((client == null || client == '') || ( client != null && redemTotal < 0)) {
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
            var total = currentOrder.getTotalTaxIncluded();
            return (total < 0.000001
            || currentOrder.getPaidTotal() + 0.000001 >= total);

        },
    });

}
;
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

    openerp_pos_loyalty(instance, module); // import openerp_pos_loyalty.js

    instance.web.client_actions.add('pos.ui',
        'instance.point_of_sale.PosWidget');
};
