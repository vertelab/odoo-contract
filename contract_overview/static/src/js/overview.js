odoo.define('contract_overview.contract_overview', function (require) {
    "use strict";

    var qweb = require('web.qweb');
    var viewRegistry = require('web.view_registry');

    const Controller = qweb.Controller.extend({
        events: _.extend({}, qweb.Controller.prototype.events, {}),
    })

    var ContractOverview = qweb.View.extend({
        withSearchBar: true,
        searchMenuTypes: ['filter', 'favorite'],

        config: _.extend({}, qweb.View.prototype.config, {
            Controller: Controller,
        }),
    });

    viewRegistry.add('contract_overview', ContractOverview);
});