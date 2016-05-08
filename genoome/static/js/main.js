(function() {
	'use strict';

	window.App = function() {
		this.init();
	};

	App.prototype.init = function() {
		var _this = this;

		window.$body = $('body');

		_this.build();
		_this.plugins();
		_this.events();
	};

	App.prototype.plugins = function($context) {
		var $genome = $('#genome-listing');
		if ($genome.length) {
			$genome.genome({
				url: $genome.data('genome-url'),
				pagination: $('#genome-navigation .pagination'),
				counter: $('#genome-navigation .page-counter'),
				perPage: $('#show')
			});
		}
	};

	App.prototype.events = function() {

	};

	App.prototype.build = function() {

	};

	$(document).on('ready', function() {
		window.app = new App();
	});

})();