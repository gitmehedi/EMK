odoo.define('report_layout.report_xlsx', function (require) {
'use strict';

var ActionManager = require('web.ActionManager');
var crash_manager = require('web.crash_manager');
var framework = require('web.framework');
var session = require('web.session');


var trigger_download_xlsx = function (session, c, action, options) {
    session.get_file({
        url: '/web/report',
        data: {action: JSON.stringify(action)},
        complete: framework.unblockUI,
        error: c.rpc_error.bind(c),
        success: function () {
            if (action && options && !action.dialog) {
                options.on_close();
            }
        },
    });
};

ActionManager.include({
    ir_actions_report_xml: function (action, options) {
        var self = this;
        action = _.clone(action);

        if (action.report_type === 'xlsx') {
            framework.blockUI();
            var c = crash_manager;
            return trigger_download_xlsx(self.session, c, action, options);
        } else {
            return self._super(action, options);
        }
    }
});

});