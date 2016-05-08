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
		//var _this = this;

		//$context = $context || $('body');

		$('.owl-carousel').owlCarousel({
			loop: true,
			margin: 0,
			items: 1,
			nav: true
		});

		var $genome = $('#genome-listing');
		if ($genome.length) {
			$genome.genome({url: $genome.data('genome-url')});
		}
	};

	App.prototype.events = function() {
		//var _this = this;

	};

	App.prototype.build = function() {

	};

	$(document).on('ready', function() {
		window.app = new App();
	});

})();