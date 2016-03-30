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
    /////

    module.Orderline = module.Orderline.extend({
        get_base_price: function () {
            var rounding = this.pos.currency.rounding;
            return round_pr((this.get_unit_price() * this.get_quantity()) - (this.get_discount() * this.get_quantity()), rounding);
        },
        get_all_prices: function () {
            //var base = round_pr(this.get_quantity() * this.get_unit_price() * (1.0 - (this.get_discount() / 100.0)), this.pos.currency.rounding);

            var base = round_pr((this.get_unit_price() * this.get_quantity()) - (this.get_discount() * this.get_quantity()), this.pos.currency.rounding);
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
            var disc = Math.min(Math.max(parseFloat(discount) || 0, 0), 100);
            this.discount = disc;
            if (actionType == 'prod_disc_fix') {
                this.discountStr = 'fix amount: ' + arguments + '';

            } else if (actionType == 'prod_disc_perc') {
                this.discountStr = ': ' + arguments + '%';

            }

            this.trigger('change', this);
        },

    });


    ////////
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


        setDiscountTotal: function (discountAmount) {
            this.discountAmount = discountAmount;
            //this.trigger('change',this);
        },
        getDiscountAmount: function () {
            return this.discountAmount;
        },

        getDisTotal: function () {
            return this.getSubtotal() - this.discountAmount;
        },

        addProduct: function (product, prodDiscPrice, actionType, arguments, options) {
            if (this._printed) {
                this.destroy();
                return this.pos.get('selectedOrder').addProduct(product);
            }
            options = options || {};
            var attr = JSON.parse(JSON.stringify(product));
            attr.pos = this.pos;
            attr.order = this;
            var line = new module.Orderline({}, {pos: this.pos, order: this, product: product});
            //set the amount for discount
            line.set_discount(prodDiscPrice, actionType, arguments);

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
            if (last_orderline && last_orderline.can_be_merged_with(line) && options.merge !== false) {
                last_orderline.merge(line);
            } else {
                this.get('orderLines').add(line);
            }
            this.selectLine(this.getLastOrderline());
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


    });
    ///////////

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
                //var category = self.pos.db.get_category_by_id(product.categ_id[0]);

                //TODO: logic for single product
                var posOrder = self.pos.get('selectedOrder');
                var orderLine = posOrder.getSelectedLine();
                var promosRulesActions = posOrder.get('pos').promos_rules_actions;
                var method = promosRulesActions[0].action_type;
                try {
                    if (method == 'prod_disc_perc' || method == 'prod_disc_fix') {
                        var posProductObject = self.applyPromotionLine(product, posOrder);
                        var prodDiscPrice = posProductObject.discountPrice;
                        var arguments = posProductObject.arguments;

                        // product['price'] = price;
                        product['discPrice'] = posProductObject.discountPrice;
                        product['discType'] = posProductObject.action_type;
                        var actionType = product['discType'];
                    }

                } catch (error) {

                }

                options.click_product_action(product, prodDiscPrice, actionType, arguments);
            };

            this.product_list = options.product_list || [];
            this.product_cache = new module.DomCache();
        },
        /*
         -Loop through the promosRuless
         -Check promotion is active or not
         -Clear existing promotion line
         -evaluate(promtion_rule, order)
         -after evaluation
         -execute_action(promos_id, order_id)
         */
        applyPromotionLine: function (product, posOrder) {
            /*
             -search for active rule
             -
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
                    //TODO: Evaluate expression
                    var result = self.evaluateLine(promosRule, posOrder, product);
                    if (result) {
                        try {
                            //Execute the action here
                            executeAction = self.executeActionsLine(promosRule, posOrder, product)
                            return executeAction;
                        } catch (error) {
                            //TODO:
                        }
                        if (promosRule.stop_further) {
                            return true;
                        }
                    }

                } else {
                    //TODO: what to do
                    console('no promotion rule set');
                }

            }

            //return true;
            return executeAction;


        },
        /*
         evaluate if the promotion is valid
         sales.py: evaluate_line()
         */
        evaluateLine: function (promosRule, posOrder, product) {

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
                if (expression.length > 0) {
                    for (var i = 0, len = expression.length; i < len; i++) {
                        var result = 'Execution Failed';
                        try {
                            //TODO: expressionEvaluateLine()
                            result = self.expressionEvaluateLine(expression[0], posOrder, product)
                            /*
                             Check: promos_rule
                             -any ,
                             -or ,
                             -stop_further
                             */
                            if ((result == expectedResult) && (logic == 'and')) {
                                return false;
                            }
                            //For OR logic any True is completely True
                            if ((result == expectedResult) && (logic == 'or')) {
                                return true;
                            }
                            if ((result == expectedResult) && promosRule.stop_further) {
                                return true;
                            }
                        } catch (error) {
                            return false;
                        }
                    }
                    if (logic == 'and') {
                        //If control comes here for and logic, then all conditions were
                        //satisfied
                        return true;
                    }

                }else{
                    return false;
                }

            } else {
                return false;
            }


        },
        executeActionsLine: function (promosRule, posOrder, product) {
            var self = this;

            //var actionObj = posOrder.get('pos').promos_rules_actions;
            var actionRuleExecute = {};

            var actionId = [];
            for (var i = 0, len = promosRule.actions.length; i < len; i++) {
                actionId.push(promosRule.actions[i]);
                return actionRuleExecute = self.executeWorkOrder(actionId[i], posOrder, product);
            }

            //for(action in promosRule.actions){
            //    try{
            //        //TODO: actionObj.execute
            //        var actionRuleExecute = self.actionRuleExecute(action.id, posOrder);
            //    }catch(error){
            //       console.log(error);
            //    }
            //}
            //return true;
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
            var partnerCatId = promosRule.partner_categories;

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
                if (partners != null) {
                    for (var i = 0, len = partnerCatId.length; i < len; i++) {
                        if (partners.id == partnerCatId[i]) {
                            return true;
                        }
                    }
                } else {
                    return true;
                }
            } else {
                return false;
            }

        },
        /*
         -Evaluate the expression in a given environment
         */
        expressionEvaluateLine: function (expression, posOrder, product) {
            //TODO: What to do
            var promosRuleExp = posOrder.get('pos').promos_rules_conditions_exps;
            for (var i = 0, len = promosRuleExp.length; i < len; i++) {
                if (promosRuleExp[i].id == expression) {
                    var serialisedExpr = promosRuleExp[i].serialised_expr;
                    return serialisedExpr;
                }

            }


            var categories = [];
            var products = [];  // List of product Codes
            //var prodQty = {};  //Dict of product_code:quantity
            var prodUnitUrice = {};
            var prodSubTotal = {};
            var prodDiscount = {};
            var prodWeight = {};
            //var prodNetPrice = {};
            var prodLines = {};

            categories.append(product.categ_id.code);
            var prod_cat = product.categ_id.code;
            var productCode = product.code;
            products.append(productCode);
            prodLines[productCode] = product;

            //var serialisedExpr = expression.serialised_expr;
            return 'False';

        },
        executeWorkOrder: function (actionId, posOrder, product) {

            var self = this;

            var discountValue = {};
            var promosRulesActions = posOrder.get('pos').promos_rules_actions;
            for (var i = 0, len = promosRulesActions.length; i < len; i++) {
                if (actionId == promosRulesActions[i].id) {
                    //promosRuleArray.push(promosRulesActions[i]);
                    var method_prefix = 'action_';
                    var method = promosRulesActions[i].action_type;
                    discountValue = self[method_prefix + method](promosRulesActions[i], product);
                    // discountValue['discountPrice'] = discountPrice;
                    //discountValue['action_type'] = promosRulesActions[i].action_type;
                    //discountValue['arguments'] = promosRulesActions[i].arguments;
                    return discountValue;
                }
            }

            return discountValue;

        },
        promotionLineDate: function (strDate) {
            //TODO: conversion on date('%Y-%m-%d %H:%M:%S' or '%Y-%m-%d')
            //return date here
            var parts = strDate.split("-");
            return new Date(parts[0], parts[1] - 1, parts[2]);

        },
        action_prod_disc_perc: function (promosRuleAction, product) {
            var self = this;
            var discountObject = {};
            var productCategory = self.pos.db.get_category_by_id(product.categ_id[0]);
            //compare the code
            var productCode = promosRuleAction.product_code;
            var categoryCode = productCategory.code;
            try {
                if (productCode.trim() == categoryCode.trim()) {
                    var discountPrice = product.price * (promosRuleAction.arguments / 100);
                    //var arguments = promosRulesAction.arguments;
                    discountObject['action_type'] = promosRuleAction.action_type;
                    discountObject['arguments'] = promosRuleAction.arguments;
                    discountObject['discountPrice'] = discountPrice;
                    return discountObject;

                }
            } catch (error) {
                alert('action_prod_disc_perc' + ' method error ');

            }


            return discountObject;


        },
        action_prod_disc_fix: function (promosRuleAction, product) {
            var self = this;
            var discountObject = {};
            var productCategory = self.pos.db.get_category_by_id(product.categ_id[0]);
            //compare the code
            var productCode = promosRuleAction.product_code;
            var categoryCode = productCategory.code;
            try {
                if (productCode == categoryCode) {
                    var discountPrice = promosRuleAction.arguments;
                    //var arguments = promosRuleAction.arguments;
                    discountObject['action_type'] = promosRuleAction.action_type;
                    discountObject['arguments'] = promosRuleAction.arguments;
                    discountObject['discountPrice'] = discountPrice;
                    return discountObject;

                }
            } catch (error) {
                alert('action_prod_disc_fix' + ' method error ');

            }
            return discountObject;

        },
        action_prod_sub_disc_perc: function () {

        },
        action_prod_sub_disc_fix: function () {

        },
        action_cat_disc_perc: function () {

        },
        action_cat_disc_fix: function () {

        },
        action_prod_x_get_y: function (promosRule, posOrder) {
            return 20;
        }
    });


//////////////////////
    module.PaypadButtonWidget.include({
        template: 'PaypadButtonWidget',

        init: function (parent, options) {
            this._super(parent, options);
            this.cashregister = options.cashregister;
        },

        renderElement: function () {
            var self = this;
            this._super();

            this.$el.click(function () {
                if (self.pos.get('selectedOrder').get('screen') === 'receipt') {  //TODO Why ?
                    console.warn('TODO should not get there...?');
                    return;
                }
                //get the order
                var posOrder = self.pos.get('selectedOrder');
                var promosRulesActions = posOrder.get('pos').promos_rules_actions;
                var method = promosRulesActions[0].action_type;
                try {
                    if (method == 'cart_disc_perc' || method == 'cart_disc_fix') {
                        var posDiscuntOrders = self.applyPromotions(posOrder);
                        posOrder.setDiscountTotal(posDiscuntOrders);
                    }
                } catch (error) {

                }
                self.pos.get('selectedOrder').addPaymentline(self.cashregister);
                self.pos_widget.screen_selector.set_current_screen('payment');
            });
        },

        //TODO: write promotion logic here
        /*
         -Loop through the promosRuless
         -Check promotion is active or not
         -Clear existing promotion line
         -evaluate(promtion_rule, order)
         -after evaluation
         -execute_action(promos_id, order_id)
         */
        applyPromotions: function (posOrder) {
            var self = this;
            var promosRules = posOrder.get('pos').promotion_rules;
            var promosRulesActions = posOrder.get('pos').promos_rules_actions;

            var executeAction = 0;
            var promotionArray = [];
            for (i = 0, len = promosRules.length; i < len; i++) {

                if (promosRules[i].active == true) {
                    promotionArray.push(promosRules[i]);
                    var promosRule = promotionArray[0];
                    var result = self.evaluates(promosRule, posOrder);
                    if (result) {
                        try {
                            executeAction = self.executeActions(promosRule, posOrder)
                            return executeAction;
                        } catch (error) {
                            //TODO:
                        }
                        if (promosRule.stop_further) {
                            return true;
                        }
                    }
                } else {
                    //TODO: what to do
                    console('no promotion rule set');
                }
            }
            return executeAction;
        },

        /*
         -evaluate if the promotion is valid
         -
         */
//result = self.expressionEvaluate(expression, posOrder)
        evaluates: function (promosRule, posOrder, product) {
            var self = this;
            var promosRuleExp = posOrder.get('pos').promos_rules_conditions_exps;
            try {
                //TODO: Check primary condition for date && partner category
                self.checkPrimaryConditions(promosRule, posOrder, product);
            } catch (error) {
                return false;
            }
            //TODO: Rules checking for expressions
            var expectedResult = promosRule.expected_logic_result;
            var logic = promosRule.logic;
            var expression = promosRule.expressions;
            for (var i = 0, len = expression.length; i < len; i++) {

                var result = 'Execution Failed';
                try {
                    result = self.expressionEvaluate(expression[0], posOrder, product)
                    //For and logic, any False is completely false
                    if ((result != expectedResult) && (logic == 'and')) {
                        return false;
                    }
                    //For OR logic any True is completely True
                    if ((result == expectedResult) && (logic == 'or')) {
                        return true;
                    }
                    if ((result == expectedResult) && promosRule.stop_further) {
                        return true;
                    }
                } catch (error) {
                    return false;
                }
            }

            if (logic == 'and') {
                //If control comes here for and logic, then all conditions were
                //satisfied
                return true;
            }

            return false;


        },

        /*
         -Executes the actions associated with this rule
         */

        executeActions: function (promosRule, posOrder) {
            var self = this;

            var actionObj = posOrder.get('pos').promos_rules_actions;

            var actionArray = [];
            for (var i = 0, len = promosRule.actions.length; i < len; i++) {
                actionArray.push(promosRule.actions[i]);
                var actionRuleExecute = self.actionRuleExecute(actionArray[0], posOrder);
            }

            //for(action in promosRule.actions){
            //    try{
            //        //TODO: actionObj.execute
            //        var actionRuleExecute = self.actionRuleExecute(action.id, posOrder);
            //    }catch(error){
            //       console.log(error);
            //    }
            //}
            //return true;
            return actionRuleExecute;


        },
        /*
         -Check this condition for
         -Valid Coupon code
         -Valid date
         */

        checkPrimaryConditions: function (promosRule, posOrder) {
            var self = this;
            /*
             Check if the customer is in the specified partner cats
             -get all the partners
             - check with partner.id = partner_cat.id
             */
            var partners = posOrder.get_client();
            var partnerCatId = promosRule.partner_categories;
            try {
                //check the date with present date
                var fromDate = promosRule.from_date;
                var toDate = promosRule.to_date;
                var date = new Date();
                var day = date.getDate();
                var month = date.getMonth() + 1;
                var year = date.getFullYear();
                var today = year + '-' + month + '-' + day;
                if (partners != null) {
                    if (self.promotionDate(today) >= self.promotionDate(fromDate)
                        && self.promotionDate(today) >= self.promotionDate(toDate)) {
                        for (var i = 0, len = partnerCatId.length; i < len; i++) {
                            try {
                                if (partners.id == partnerCatId[i]) {
                                    console.log('successfulllll');
                                    return true;
                                }
                            } catch (error) {
                                console.log('not applicable for promotion');
                                return false;
                            }
                        }

                    }
                }

            } catch (error) {
                console.log('null pointer exception');
                return false;
            }
            //TODO: Coupon code logic will be here


            return true;

        },


        /*
         -Evaluates the expression in given environment
         */

        expressionEvaluate: function (expression, posOrder, product) {


            var promosRuleExp = posOrder.get('pos').promos_rules_conditions_exps;
            for (var i = 0, len = promosRuleExp.length; i < len; i++) {
                if (promosRuleExp[i].id == expression) {
                    var serialisedExpr = promosRuleExp[i].serialised_expr;
                    return 'True';
                }

            }

            /*
             var products = []  // List of product Codes
             var prodQty = {}  //Dict of product_code:quantity
             var prodUnitUrice = {}
             var prodSubTotal = {}
             var prodDiscount = {}
             var prodWeight = {}
             //var prodNetPrice = {}
             var prodLines = {}

             for (line in posOrder.order_line) {
             if (line.product_id) {
             var product_code = line.product_id.code

             products.append(product_code);
             prodLines[product_code] = line.product_id;
             prodQty[product_code] = prodQty.get(product_code, 0.00) + line.product_uom_qty;
             prodUnitUrice[product_code] = prodUnitUrice.get(product_code, 0.00) + line.price_unit;
             prodSubTotal[product_code] = prodSubTotal.get(product_code, 0.00) + line.price_subtotal;
             prodDiscount[product_code] = prodDiscount.get(product_code, 0.00) + line.discount;
             prodWeight[product_code] = prodWeight.get(product_code, 0.00) + line.th_weight;

             }

             }*/
            //TODO: what is return eval(expression.serialised_expr)
            //var serialisedExpr = expression.serialised_expr;
            return 'False';

        },

        /*
         - Converts string date to date
         */
        promotionDate: function (strDate) {
            //TODO: conversion on date('%Y-%m-%d %H:%M:%S' or '%Y-%m-%d')
            //return date here
            var parts = strDate.split("-");
            return new Date(parts[0], parts[1] - 1, parts[2]);
        },

        /*
         -This function count the number of sale orders(not in cancelled state)
         that are linked to a particular coupon.
         */

        countCouponUse: function (promosRules, posOrder) {
            var self = this;
            //var promosRuless = posOrder.get('pos').promotion_rule;

            var res = {};
            for (promosRules in promosRules) {
                var matchingIds = [];
                if (promosRules.coupon_code) {
                    //If there is uses per coupon defined check if its overused
                    //TODO:  what is search
                    if (promosRule.uses_per_coupon > -1) {
                        for (var i = 0, len = posOrder.length; i < len; i++) {
                            if (posOrder.coupon_code == promosRule.coupon_code && posOrder.state != 'cancel') {
                                matchingIds = posOrder;
                            }
                        }
                        //matching_ids = posOrder.search([('coupon_code', '=', promotion_rule.coupon_code), ('state', '<>', 'cancel')])
                    }
                }
                res[promosRule.id] = matchingIds.length;
            }
            return res;

        },

        /*
         -Executes the action into the order
         */

        actionRuleExecute: function (actionId, posOrder) {
            //TODO: Order rule calculation will be here
            var self = this;

            //var discountValue = 0;
            var promosRulesActions = posOrder.get('pos').promos_rules_actions;
            var promosRuleArray = [];

            for (var i = 0, len = promosRulesActions.length; i < len; i++) {
                if (actionId == promosRulesActions[i].id) {
                    //promosRuleArray.push(promosRulesActions[i]);
                    var method_prefix = 'action_';
                    var method = promosRulesActions[i].action_type;
                    var discountValue = self[method_prefix + method](promosRulesActions[i], posOrder);
                }
            }


            //TODO: promosRulesActions need to be dynamic
            /* if (actionId == promosRuleArray[0].id) {
             var method_prefix = 'action_';
             var method = promosRulesActions[0].action_type;
             var discountValue = self[method_prefix + method](promosRulesActions, posOrder);

             }*/
            return discountValue;

        },
        action_cart_disc_fix: function (promosRulesActions, posOrder) {
            var subTotal = posOrder.getSubtotal();
            var discountAmount = promosRulesActions.arguments;

            return discountAmount;

        },
        action_cart_disc_perc: function (promosRulesActions, posOrder) {
            var subTotal = posOrder.getSubtotal();

            var discountAmount = subTotal * (promosRulesActions.arguments / 100);

            return discountAmount;
        },

    });
    module.ProductScreenWidget.include({
        start: function () { //FIXME this should work as renderElement... but then the categories aren't properly set. explore why
            var self = this;

            this.product_list_widget = new module.ProductListWidget(this, {
                click_product_action: function (product, prodDiscPrice, actionType, arguments) {
                    if (product.to_weight && self.pos.config.iface_electronic_scale) {
                        self.pos_widget.screen_selector.set_current_screen('scale', {product: product});
                    } else {
                        self.pos.get('selectedOrder').addProduct(product, prodDiscPrice, actionType, arguments);
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