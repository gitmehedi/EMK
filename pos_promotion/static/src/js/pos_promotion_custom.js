function openerp_pos_promotion(instance, module) { // module is
    // instance.point_of_sale
    var QWeb = instance.web.qweb;
    var _t = instance.web._t;

    var round_di = instance.web.round_decimals;
    var round_pr = instance.web.round_precision;

    /*
     * All code will be here
     */
    module.PosModel = module.PosModel.extend({

        // Server side model loaders. This is the list of the models that need to be loaded from
        // the server. The models are loaded one by one by this list's order. The 'loaded' callback
        // is used to store the data in the appropriate place once it has been loaded. This callback
        // can return a deferred that will pause the loading of the next module.
        // a shared temporary dictionary is available for loaders to communicate private variables
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
            }, {
                model: 'res.company',
                fields: ['currency_id', 'email', 'website', 'company_registry', 'vat', 'name', 'phone', 'partner_id', 'country_id', 'tax_calculation_rounding_method'],
                ids: function (self) {
                    return [self.user.company_id[0]]
                },
                loaded: function (self, companies) {
                    self.company = companies[0];
                },
            }, {
                model: 'decimal.precision',
                fields: ['name', 'digits'],
                loaded: function (self, dps) {
                    self.dp = {};
                    for (var i = 0; i < dps.length; i++) {
                        self.dp[dps[i].name] = dps[i].digits;
                    }
                },
            }, {
                model: 'product.uom',
                fields: [],
                domain: null,
                context: function (self) {
                    return {active_test: false};
                },
                loaded: function (self, units) {
                    self.units = units;
                    var units_by_id = {};
                    for (var i = 0, len = units.length; i < len; i++) {
                        units_by_id[units[i].id] = units[i];
                        units[i].groupable = ( units[i].category_id[0] === 1 );
                        units[i].is_unit = ( units[i].id === 1 );
                    }
                    self.units_by_id = units_by_id;
                }
            }, {
                model: 'res.users',
                fields: ['name', 'ean13'],
                domain: null,
                loaded: function (self, users) {
                    self.users = users;
                },
            }, {
                model: 'res.partner',
                fields: ['name', 'street', 'city', 'state_id', 'country_id', 'vat', 'phone', 'zip', 'mobile', 'email', 'ean13', 'write_date', 'category_id'],
                domain: [['customer', '=', true]],
                loaded: function (self, partners) {
                    self.partners = partners;
                    self.db.add_partners(partners);
                },
            }, {
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
            }, {
                model: 'account.tax',
                fields: ['name', 'amount', 'price_include', 'include_base_amount', 'type', 'child_ids', 'child_depend', 'include_base_amount'],
                domain: null,
                loaded: function (self, taxes) {
                    self.taxes = taxes;
                    self.taxes_by_id = {};
                    _.each(taxes, function (tax) {
                        self.taxes_by_id[tax.id] = tax;
                    });
                    _.each(self.taxes_by_id, function (tax) {
                        tax.child_taxes = {};
                        _.each(tax.child_ids, function (child_tax_id) {
                            tax.child_taxes[child_tax_id] = self.taxes_by_id[child_tax_id];
                        });
                    });
                },
            }, {
                model: 'pos.session',
                fields: ['id', 'journal_ids', 'name', 'user_id', 'config_id', 'start_at', 'stop_at', 'sequence_number', 'login_number'],
                domain: function (self) {
                    return [['state', '=', 'opened'], ['user_id', '=', self.session.uid]];
                },
                loaded: function (self, pos_sessions) {
                    self.pos_session = pos_sessions[0];

                    var orders = self.db.get_orders();
                    for (var i = 0; i < orders.length; i++) {
                        self.pos_session.sequence_number = Math.max(self.pos_session.sequence_number, orders[i].data.sequence_number + 1);
                    }
                },
            }, {
                model: 'pos.config',
                fields: [],
                domain: function (self) {
                    return [['id', '=', self.pos_session.config_id[0]]];
                },
                loaded: function (self, configs) {
                    self.config = configs[0];
                    self.config.use_proxy = self.config.iface_payment_terminal ||
                        self.config.iface_electronic_scale ||
                        self.config.iface_print_via_proxy ||
                        self.config.iface_scan_via_proxy ||
                        self.config.iface_cashdrawer;

                    self.barcode_reader.add_barcode_patterns({
                        'product': self.config.barcode_product,
                        'cashier': self.config.barcode_cashier,
                        'client': self.config.barcode_customer,
                        'weight': self.config.barcode_weight,
                        'discount': self.config.barcode_discount,
                        'price': self.config.barcode_price,
                    });

                    if (self.config.company_id[0] !== self.user.company_id[0]) {
                        throw new Error(_t("Error: The Point of Sale User must belong to the same company as the Point of Sale. You are probably trying to load the point of sale as an administrator in a multi-company setup, with the administrator account set to the wrong company."));
                    }
                },
            }, {
                model: 'stock.location',
                fields: [],
                ids: function (self) {
                    return [self.config.stock_location_id[0]];
                },
                loaded: function (self, locations) {
                    self.shop = locations[0];
                },
            }, {
                model: 'product.pricelist',
                fields: ['currency_id'],
                ids: function (self) {
                    return [self.config.pricelist_id[0]];
                },
                loaded: function (self, pricelists) {
                    self.pricelist = pricelists[0];
                },
            }, {
                model: 'res.currency',
                fields: ['name', 'symbol', 'position', 'rounding', 'accuracy'],
                ids: function (self) {
                    return [self.pricelist.currency_id[0]];
                },
                loaded: function (self, currencies) {
                    self.currency = currencies[0];
                    if (self.currency.rounding > 0) {
                        self.currency.decimals = Math.ceil(Math.log(1.0 / self.currency.rounding) / Math.log(10));
                    } else {
                        self.currency.decimals = 0;
                    }

                },
            }, {
                model: 'product.packaging',
                fields: ['ean', 'product_tmpl_id'],
                domain: null,
                loaded: function (self, packagings) {
                    self.db.add_packagings(packagings);
                },
            }, {
                model: 'pos.category',
                fields: ['id', 'name', 'parent_id', 'child_id', 'image', 'code'],
                domain: null,
                loaded: function (self, categories) {
                    self.db.add_categories(categories);
                },
            }, {
                model: 'product.product',
                fields: ['display_name', 'list_price', 'price', 'pos_categ_id', 'taxes_id', 'ean13', 'default_code',
                    'to_weight', 'uom_id', 'uos_id', 'uos_coeff', 'mes_type', 'description_sale', 'description',
                    'product_tmpl_id', 'categ_id'],
                domain: [['sale_ok', '=', true], ['available_in_pos', '=', true]],
                context: function (self) {
                    return {pricelist: self.pricelist.id, display_default_code: false};
                },
                loaded: function (self, products) {
                    self.db.add_products(products);
                },
            }, {
                model: 'account.bank.statement',
                fields: ['account_id', 'currency', 'journal_id', 'state', 'name', 'user_id', 'pos_session_id'],
                domain: function (self) {
                    return [['state', '=', 'open'], ['pos_session_id', '=', self.pos_session.id]];
                },
                loaded: function (self, bankstatements, tmp) {
                    self.bankstatements = bankstatements;

                    tmp.journals = [];
                    _.each(bankstatements, function (statement) {
                        tmp.journals.push(statement.journal_id[0]);
                    });
                },
            }, {
                model: 'account.journal',
                fields: [],
                domain: function (self, tmp) {
                    return [['id', 'in', tmp.journals]];
                },
                loaded: function (self, journals) {
                    self.journals = journals;

                    // associate the bank statements with their journals.
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
            /*
             * promotion rules model are added here
             * model: promos.rule
             * model: promos.rules.conditions.exps
             * model: promos.rules.actions
             */

            {
                model: 'promos.rules',
                fields: [],
                loaded: function (self, promotion_rules) {
                    self.promotion_rules = promotion_rules;
                    console.log(' rules:: ' + JSON.stringify(self.promotion_rules));
                }
            }, {
                model: 'promos.rules.conditions.exps',
                fields: [],
                loaded: function (self, promos_rules_conditions_exps) {
                    self.promos_rules_conditions_exps = promos_rules_conditions_exps;
                    console.log(' conditions:: ' + JSON.stringify(self.promos_rules_conditions_exps));
                }
            }, {
                model: 'promos.rules.actions',
                fields: [],
                loaded: function (self, promos_rules_actions) {
                    self.promos_rules_actions = promos_rules_actions;
                    console.log(' actions:: ' + JSON.stringify(self.promos_rules_actions));
                }
            }, {
                model: 'res.partner.category',
                fields: [],
                loaded: function (self, res_partner_category) {
                    self.res_partner_category = res_partner_category;
                    //console.log(' category:: ' + JSON.stringify(self.res_partner_category));
                }
            }, {
                model: 'promotion.groups',
                fields: [],
                loaded: function (self, promotion_groups) {
                    self.promotion_groups = promotion_groups;
                    //console.log(' group:: ' + JSON.stringify(self.promotion_groups));
                }
            }, {
                label: 'fonts',
                loaded: function (self) {
                    var fonts_loaded = new $.Deferred();

                    // Waiting for fonts to be loaded to prevent receipt printing
                    // from printing empty receipt while loading Inconsolata
                    // ( The font used for the receipt )
                    waitForWebfonts(['Lato', 'Inconsolata'], function () {
                        fonts_loaded.resolve();
                    });

                    // The JS used to detect font loading is not 100% robust, so
                    // do not wait more than 5sec
                    setTimeout(function () {
                        fonts_loaded.resolve();
                    }, 5000);

                    return fonts_loaded;
                },
            }, {
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
                        ctx.drawImage(self.company_logo, 0, 0, width, height);

                        self.company_logo_base64 = c.toDataURL();
                        logo_loaded.resolve();
                    };
                    self.company_logo.onerror = function () {
                        logo_loaded.reject();
                    };
                    self.company_logo.crossOrigin = "anonymous";
                    self.company_logo.src = '/web/binary/company_logo' + '?_' + Math.random();

                    return logo_loaded;
                },
            },
        ],


        // loads all the needed data on the sever. returns a deferred indicating when all the data has loaded.
        load_server_data: function () {
            var self = this;
            var loaded = new $.Deferred();
            var progress = 0;
            var progress_step = 1.0 / self.models.length;
            var tmp = {}; // this is used to share a temporary state between models loaders

            function load_model(index) {
                if (index >= self.models.length) {
                    loaded.resolve();
                } else {
                    var model = self.models[index];
                    self.pos_widget.loading_message(_t('Loading') + ' ' + (model.label || model.model || ''), progress);
                    var fields = typeof model.fields === 'function' ? model.fields(self, tmp) : model.fields;
                    var domain = typeof model.domain === 'function' ? model.domain(self, tmp) : model.domain;
                    var context = typeof model.context === 'function' ? model.context(self, tmp) : model.context;
                    var ids = typeof model.ids === 'function' ? model.ids(self, tmp) : model.ids;
                    progress += progress_step;


                    if (model.model) {
                        if (model.ids) {
                            var records = new instance.web.Model(model.model).call('read', [ids, fields], context);
                        } else {
                            var records = new instance.web.Model(model.model).query(fields).filter(domain).context(context).all()
                        }
                        records.then(function (result) {
                            try {    // catching exceptions in model.loaded(...)
                                $.when(model.loaded(self, result, tmp))
                                    .then(function () {
                                            load_model(index + 1);
                                        },
                                        function (err) {
                                            loaded.reject(err);
                                        });
                            } catch (err) {
                                loaded.reject(err);
                            }
                        }, function (err) {
                            loaded.reject(err);
                        });
                    } else if (model.loaded) {
                        try {    // catching exceptions in model.loaded(...)
                            $.when(model.loaded(self, tmp))
                                .then(function () {
                                        load_model(index + 1);
                                    },
                                    function (err) {
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
        }
    });

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


        get_base_price: function () {
            var rounding = this.pos.currency.rounding;
            var promos_rules_actions = this.pos.promos_rules_actions;
            var orderLine = this.discountAmount;
            if (promos_rules_actions !== undefined && promos_rules_actions.length > 0) {

                if (promos_rules_actions[0].action_type == 'prod_sub_disc_perc') {
                    return round_pr(((this.get_unit_price() * this.get_quantity()) - (this.get_arguments())), rounding);
                } else if (promos_rules_actions[0].action_type == 'prod_sub_disc_fix') {
                    return round_pr(((this.get_unit_price() * this.get_quantity()) - this.get_arguments()), rounding);
                } else if (promos_rules_actions[0].action_type == 'cart_disc_perc' || promos_rules_actions[0].action_type == 'cart_disc_fix') {
                    return round_pr((this.get_unit_price() * this.get_quantity()), rounding);
                } else {
                    //return round_pr((this.get_unit_price() * this.get_quantity()) - (this.get_discount() * this.get_quantity()), rounding);
                    return round_pr(((this.get_unit_price() * this.get_quantity()) - (this.get_discount())), rounding);
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
            if (actionType == 'prod_disc_fix' || actionType == 'cat_disc_fix') {
                this.discountStr = 'fix amount: ' + arguments + '';

            } else if (actionType == 'prod_disc_perc' || actionType == 'cat_disc_perc') {
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
                this.set_arguments(discount, actionType, arguments);
            }

        },
        customMerge: function (product, actionType, discountPrice, arguments) {

            var posOrder = this.pos.get('selectedOrder');
            var discount = discountPrice;

            if (actionType == 'prod_disc_fix' || actionType == 'cat_disc_fix') {
                this.set_discount(discount, actionType, arguments);
            } else if (actionType == 'prod_disc_perc' || actionType == 'cat_disc_perc') {
                this.set_discount(discount, actionType, arguments);
            }
            else if (actionType == 'prod_sub_disc_perc' || actionType == 'prod_sub_disc_fix') {
                //this.set_discount(orderline.discount, actionType, arguments);
                this.set_arguments(discount, actionType, arguments);
            } else if (actionType == 'cart_disc_perc' || actionType == 'cart_disc_perc') {
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
            this.discountAmount = 0;

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
        setDiscountAmount: function (discountAmount) {
            this.discountAmount = discountAmount;
            //this.trigger('change',this);
        },
        getDiscountAmount: function () {
            return this.discountAmount;
        },

        getDisTotal: function () {
            return this.getSubtotal()>0? (this.getSubtotal()- this.discountAmount):0;
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
            if (actionType !== 'prod_sub_disc_perc' || actionType !== 'prod_sub_disc_fix' ) {
                line.set_discount(prodDiscPrice, actionType, arguments);

            }

            if (actionType == 'prod_sub_disc_perc' || actionType == 'prod_sub_disc_fix') {

                line.set_arguments(prodDiscPrice, actionType, arguments);
            }

            if (last_orderline && last_orderline.can_be_merged_with(line) && options.merge !== false) {
                last_orderline.merge(line, actionType, arguments);
            }else {
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
                amount_total: this.getTotalTaxIncluded(),
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
                discount_type: 'percent',
                percent_discount: 10,
            };
        },
        currentSubtotal: function (posOrder, product, cart_quantity, promosRulesAction) {
            var selectedOrderLine = this.pos.get('selectedOrder').selected_orderline;
            var prevSubTotal = 0;
            var currentSubTotal = 0;
            var storeSubTotal = 0;
            var actionType = promosRulesAction.action_type;
            if (selectedOrderLine != undefined && (actionType == 'cart_disc_perc' || actionType == 'cart_disc_fix')) {
                var currentPrice = product.price;
                var currentOrderLinePrice = 0;
                var sum = 0;

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
            else if (selectedOrderLine != undefined & (actionType == 'cat_disc_perc' || actionType == 'cat_disc_fix' || actionType == 'prod_disc_perc' || actionType == 'prod_disc_fix')) {
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

            } else {
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
        applyPromotionLine: function (product, posOrder, cart_quantity, promosRulesActionObject) {
            /*
             -search for active rule
             */
            var self = this;
            var promosRules = posOrder.get('pos').promotion_rules;
            //var promosRulesActions = posOrder.get('pos').promos_rules_actions;
            var executeAction = {};
            var promotionArray = [];
            for (i = 0, len = promosRules.length; i < len; i++) {

                if (promosRules[i].active == true) {

                    promotionArray.push(promosRules[i]);
                    var promosRule = promotionArray[0];
                    var result = self.evaluateLine(promosRule, posOrder, product, cart_quantity, promosRulesActionObject);
                    if (result) {
                        try {
                            //Execute the action here
                            executeAction = self.executeActionsLine(promosRule, posOrder, product, cart_quantity, promosRulesActionObject)
                            return executeAction;
                        } catch (error) {
                            //TODO:
                        }
                        if (promosRule.stop_further) {
                            return true;
                        }
                    }
                } else {
                    console('no promotion rule set');
                }
            }
            return false;
        },
        /*
         evaluate if the promotion is valid
         sales.py: evaluate_line()
         */
        evaluateLine: function (promosRule, posOrder, product, cart_quantity, promosRulesActionObject) {

            var self = this;
            var promosRuleExp = posOrder.get('pos').promos_rules_conditions_exps;
            try {
                /*
                 will check Date and partner category
                 -return true if condition is satisfied
                 -return false if condition is not satisfied
                 */
                var primaryCondition = self.checkPrimaryConditionsLine(promosRule, posOrder);
            } catch (error) {
                return false;
            }
            if (primaryCondition) {

                var expectedResult = promosRule.expected_logic_result;
                var logic = promosRule.logic;
                var expression = promosRule.expressions;
                var flag = false;
                if (expression.length > 0) {
                    for (var i = 0, len = expression.length; i < len; i++) {
                        var result = 'Execution Failed';
                        try {
                            result = self.expressionEvaluateLine(expression[0], posOrder, product, cart_quantity, promosRulesActionObject[0])
                            flag = false;
                            if ((result.toLowerCase() == expectedResult.toLowerCase()) && (logic == 'and')) {
                                flag = true;
                            }
                            //For OR logic any True is completely True
                            else if ((result.toLowerCase() == expectedResult.toLowerCase()) && (logic == 'or')) {
                                return true;
                            }
                            else if ((result.toLowerCase() == expectedResult.toLowerCase()) && promosRule.stop_further) {
                                return true;
                            }
                        } catch (error) {
                            return false;
                        }
                    }
                    //if (logic == 'and') {
                    //    //If control comes here for and logic, then all conditions were
                    //    //satisfied
                    //    return true;
                    //}

                } else {
                    return false;
                }

            } else {
                return false;
            }
            if (flag == true) {
                return true;
            }
            return false;
        },
        executeActionsLine: function (promosRule, posOrder, product, cart_quantity, promosRulesActionObject) {
            var self = this;
            var actionRuleExecute = {};
            var actionId = [];
            for (var i = 0, len = promosRule.actions.length; i < len; i++) {
                actionId.push(promosRule.actions[i]);
                return actionRuleExecute = self.executeWorkOrder(actionId[i], posOrder, product, cart_quantity, promosRulesActionObject);
            }
            return actionRuleExecute;
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
            if (self.promotionLineDate(today) >= self.promotionLineDate(fromDate)
                && self.promotionLineDate(today) <= self.promotionLineDate(toDate)) {
                if (partners != null && partnerCategorys.length > 0) {// promotion apply for particular user
                    for (var i = 0, len = partnerCategorys.length; i < len; i++) {
                        if (partners.id == partnerCategorys[i]) {
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

        },
        /*
         -Evaluate the expression in a given environment
         */
        expressionEvaluateLine: function (expression, posOrder, product, cart_quantity, promosRulesAction) {
            var self = this;
            var promosRuleExp = posOrder.get('pos').promos_rules_conditions_exps;
            var currentSubTotal = this.currentSubtotal(posOrder, product, cart_quantity, promosRulesAction);
            var category = self.pos.db.get_category_by_id(product.pos_categ_id[0]);

            var var_true = 'True';
            var var_false = 'False';
            for (var i = 0, len = promosRuleExp.length; i < len; i++) {
                if (promosRuleExp[i].id == expression) {
                    var exp = promosRuleExp[i];

                    var expValue = exp.value;
                    if (expValue == product.default_code || expValue == category.code || currentSubTotal >= expValue) {
                        var comparator = exp.comparator;
                        if (comparator == '==' && cart_quantity == exp.quantity || (comparator == '==' && currentSubTotal == expValue)) {
                            return var_true;
                        }
                        else if (comparator == '>=' && cart_quantity >= exp.quantity || (comparator == '>=' && currentSubTotal >= expValue)) {
                            return var_true;
                        }
                        else if (comparator == '<=' && cart_quantity <= exp.quantity || (comparator == '<=' && currentSubTotal <= expValue)) {
                            return var_true;
                        }
                        else if (comparator == '!=' && cart_quantity != exp.quantity || (comparator == '!=' && currentSubTotal != expValue)) {
                            return var_true;
                        }
                        else if (comparator == '>' && cart_quantity > exp.quantity || (comparator == '>' && currentSubTotal > expValue)) {
                            return var_true;
                        }
                        else if (comparator == '<' && cart_quantity < exp.quantity || (comparator == '<' && currentSubTotal < expValue)) {
                            return var_true;
                        }
                        else {
                            return var_false;
                        }
                    }
                } else {
                    return var_false;
                }
            }
            return var_false;

        },
        executeWorkOrder: function (actionId, posOrder, product, cart_quantity, promosRulesActionObject) {

            var self = this;
            var discountObject = {};
            var promosRulesActions = promosRulesActionObject[0];
            for (var i = 0, len = promosRulesActionObject.length; i < len; i++) {
                if (actionId == promosRulesActions.id) {
                    //promosRuleArray.push(promosRulesActions[i]);
                    var method_prefix = 'action_';
                    var method = promosRulesActions.action_type;
                    discountObject = self[method_prefix + method](promosRulesActions, posOrder, product, cart_quantity);

                    return discountObject;
                }
            }
            return discountObject;
        },
        promotionLineDate: function (strDate) {
            var parts = strDate.split("-");

            return new Date(parts[0], parts[1] - 1, parts[2]);
        },
        action_prod_disc_perc: function (promosRuleAction, posOrder, product, cart_quantity) {

            var discountObject = {};
            discountObject = this.discountCalculationPerc(promosRuleAction, product, cart_quantity);

            return discountObject;
        },
        action_prod_disc_fix: function (promosRuleAction, posOrder, product, cart_quantity) {

            var discountObject = {};
            discountObject = this.discountCalculationFix(promosRuleAction, product, cart_quantity);

            return discountObject;
        },
        action_prod_sub_disc_perc: function (promosRuleAction, posOrder, product, cart_quantity) {

            var discountObject = {};
            discountObject = this.discountCalculationPerc(promosRuleAction, product, cart_quantity);

            return discountObject;
        },
        action_prod_sub_disc_fix: function (promosRuleAction, posOrder, product, cart_quantity) {

            var discountObject = {};
            discountObject = this.discountCalculationSubFix(promosRuleAction, product, cart_quantity);

            return discountObject;
        },
        action_cat_disc_perc: function (promosRuleAction, posOrder, product, cart_quantity) {

            var discountObject = {};
            discountObject = this.discountCalculationPerc(promosRuleAction, product, cart_quantity);

            return discountObject;
        },

        action_cat_disc_fix: function (promosRuleAction, posOrder, product, cart_quantity) {

            var discountObject = {};
            discountObject = this.discountCalculationFix(promosRuleAction, product, cart_quantity);

            return discountObject;
        },
        /*
         -discount on subtotal
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

            var currentSubTotal = this.currentSubtotal(posOrder, product, cart_quantity, promosRulesAction);
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
        action_prod_x_get_y: function (promosRule, posOrder) {
            return 20;
        }
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
                var category = self.pos.db.get_category_by_id(product.pos_categ_id[0]);
                //var category = self.pos.db.get_category_by_id(product.pos_categ_id[0]);
                var posOrder = self.pos.get('selectedOrder');
                var promosRulesActionObject = posOrder.get('pos').promos_rules_actions;
                var promosRulesActions = promosRulesActionObject[0];
                var promosRuleExp = posOrder.get('pos').promos_rules_conditions_exps;

                var orderLine = posOrder.getSelectedLine();
                var cart_quantity = 1;
                var splitArray = [];
                var promosExpCodeSplit = promosRuleExp[0].value.split(',');
                if (promosRulesActions.action_type == "cart_disc_perc" || promosRulesActions.action_type == "cart_disc_fix") {
                    if (orderLine == undefined) {
                        cart_quantity = 1;

                    } else if (product.id == orderLine.product.id) {
                        cart_quantity = orderLine.quantity + 1;

                    } else {
                        cart_quantity = 1;

                    }
                } else {
                    var count = 0;
                    for (var i = 0, len = promosExpCodeSplit.length; len > i; i++) {
                        if ((orderLine == undefined && category.code == promosExpCodeSplit[i]) || (orderLine == undefined && product.default_code == promosExpCodeSplit[i])) {
                            splitArray.push(promosExpCodeSplit[i]);
                            cart_quantity = 1;

                        } else if ((orderLine != undefined && category.code == promosExpCodeSplit[i] && product.id == orderLine.product.id) || (orderLine != undefined && product.default_code == promosExpCodeSplit[i] && product.id == orderLine.product.id)) {
                            splitArray.push(promosExpCodeSplit[i]);
                            cart_quantity = orderLine.quantity + 1;

                        } else if ((orderLine != undefined && category.code == promosExpCodeSplit[i] && product.id !== orderLine.product.id) || (orderLine != undefined && product.default_code == promosExpCodeSplit[i] && product.id != orderLine.product.id)) {
                            if (count == 0) {
                                splitArray.push(promosExpCodeSplit[i]);
                                cart_quantity = 1;
                                count = count + 1;

                            } else {
                                splitArray.push(promosExpCodeSplit[i]);
                                cart_quantity = orderLine.quantity + 1;

                            }
                        }

                    }
                }
                var actionType = "";
                var arguments = "";
                var prodDiscPrice = "";

                if (promosRulesActionObject !== undefined && promosRulesActionObject.length > 0) {
                    try {
                        var posProductObject = {};
                        var method = promosRulesActionObject[0].action_type;
                        if (method == 'prod_disc_perc' || method == 'prod_disc_fix' || method == 'cat_disc_perc' || method == 'cat_disc_fix' || method == 'prod_sub_disc_fix' || method == 'prod_sub_disc_perc') {
                            posProductObject = posOrder.applyPromotionLine(product, posOrder, cart_quantity, promosRulesActionObject);

                            if (posProductObject != false) {
                                prodDiscPrice = posProductObject.discountPrice;
                                arguments = posProductObject.arguments;
                                product['discPrice'] = posProductObject.discountPrice;
                                product['discType'] = posProductObject.action_type;
                                product['arguments'] = posProductObject.arguments;
                                actionType = product['discType'];
                            }
                        } else if (method == 'cart_disc_perc' || method == 'cart_disc_fix') {
                            posProductObject = posOrder.applyPromotionLine(product, posOrder, cart_quantity, promosRulesActionObject);

                            if (posProductObject != false) {

                                prodDiscPrice = posProductObject.discountPrice;
                                arguments = posProductObject.arguments;
                                product['discPrice'] = posProductObject.discountPrice;
                                product['discType'] = posProductObject.action_type;
                                product['arguments'] = posProductObject.arguments;
                                actionType = product['discType'];
                                posOrder.setDiscountAmount(prodDiscPrice);
                            }
                        }
                    } catch (error) {
                    }
                }
                options.click_product_action(product, prodDiscPrice, actionType, arguments, promosRulesActions[0]);
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
            var promosRulesActionObject = posOrder.get('pos').promos_rules_actions;
            var orderLine = posOrder.selected_orderline;
            if (this.editable && posOrder.getSelectedLine() && cart_quantity != '') {
                var product = orderLine.product;
                var mode = this.numpad_state.get('mode');
                if (mode === 'quantity') {
                    var promotionObject = posOrder.applyPromotionLine(product, posOrder, cart_quantity, promosRulesActionObject);

                    var actionType = promotionObject.action_type;
                    var arguments = promotionObject.arguments;
                    var discountPrice = promotionObject.discountPrice;
                    orderLine.customMerge(product, actionType, discountPrice, arguments);
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
                var total = order ? order.getCustomTotalTaxIncluded() : 0;
                var taxes = order ? total - order.getTotalTaxExcluded() : 0;
                var method = promosRulesActions[0].action_type;

                if (method == 'cart_disc_perc' || method == 'cart_disc_fix' || method == 'prod_disc_perc' || method == 'prod_disc_fix' || method == 'cat_disc_perc' || method == 'cat_disc_fix' || method == 'prod_sub_disc_perc' || method == 'prod_sub_disc_fix') {
                    var totalWithDiscount = order.getDisTotal();
                    this.el.querySelector('.summary .total div > .value').textContent = this.format_currency(total);
                    this.el.querySelector('.summary .total div > .total_value').textContent = this.format_currency(totalWithDiscount);
                    this.el.querySelector('.summary .total .subentry .value').textContent = this.format_currency(taxes);
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


};

/*
 * custom js file module need to be
 * added here
 * i.e: openerp_pos_promotion(instance, module);
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

    openerp_pos_promotion(instance, module); // import openerp_pos_promotion.js

    instance.web.client_actions.add('pos.ui',
        'instance.point_of_sale.PosWidget');
};