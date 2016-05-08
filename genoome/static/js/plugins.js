// Avoid `console` errors in browsers that lack a console.
(function() {
	var method;
	var noop = function() {};
	var methods = [
		'assert', 'clear', 'count', 'debug', 'dir', 'dirxml', 'error',
		'exception', 'group', 'groupCollapsed', 'groupEnd', 'info', 'log',
		'markTimeline', 'profile', 'profileEnd', 'table', 'time', 'timeEnd',
		'timeline', 'timelineEnd', 'timeStamp', 'trace', 'warn'
	];
	var length = methods.length;
	var console = (window.console = window.console || {});

	while (length--) {
		method = methods[length];

		// Only stub undefined methods.
		if (!console[method]) {
			console[method] = noop;
		}
	}
}());

(function () {
	"use strict";

	var Accordion = function(node, options) {
		var defaults = {
			fold : false
		};
		this.options = $.extend({}, defaults, options);
		this.$node = $(node);
		this.init();
		this.events();
	};

	Accordion.prototype.init = function() {
		var _this = this;

		_this.resize();
	};

	Accordion.prototype.events = function() {
		var _this = this;

		_this.$node.find('.acc-switch').on('click', function() {
			var $trigger = $(this),
				$item = $trigger.parents('.acc');

			$item.toggleClass('open');
			if ($item.hasClass('open')) {
				var $content = $item.find('.acc-content');

				if ($trigger.hasClass('loaded')) {
					$content.height(_this.setHeight($(this)));
				} else {
					var url = $trigger.attr('data-url');

					$content.load(url, function(){
						$content.height(_this.setHeight($(this)));
						$trigger.addClass('loaded');
					});
				}
			} else {
				$item.find('.acc-content').height(0);
			}

			if (_this.options.fold) {
				var $siblings = _this.$node.find('.acc-switch').not(this);
				$siblings.each(function() {
					$item.removeClass('open');
					$item.find('.acc-content').height(0);
				});
			}

			return false;
		});

		_this.$node.find('.acc-open-all').on('click', function() {
			_this.$node.find('.acc')
				.addClass('open')
				.each(function(){
					var $item = $(this);
					$item.find('.acc-content').height(_this.setHeight($item.find('.acc-switch')));
				});

			return false;
		});

		$(window).on('resize', function() {
			_this.resize();
		});
	};

	Accordion.prototype.resize = function() {
		var _this = this;

		_this.$node.find('.acc.open > a').each(function() {
			$(this).parents('.acc').find('.acc-content').height(_this.setHeight($(this)));
		});
	};

	Accordion.prototype.setHeight = function($node) {
		var h = 0;
		$node.parents('.acc').find('.acc-content').children().each(function() {
			h += $(this).outerHeight(true);
		});
		return h;
	};

	$.fn.accordion = function(options) {
		return $(this).each(function(){
			new Accordion(this, options);
		});
	};

})();

(function ( $, window, document, undefined ) {

	var defaults = {
		url: 'data/genome-data.json'
	};

	function Genome( element, options ) {
		this.options = $.extend( {}, defaults, options) ;
		this._defaults = defaults;
		this.el = element;
		this.$el = $(element);

		this.init();
	}

	Genome.prototype.init = function () {
		var _this = this;

		$.getJSON(_this.options.url, function(data) {
			var html = '';

			for (var i in data.data) {
				if (data.data.hasOwnProperty(i)) {
					var item = data.data[i];

					html += '<div class="acc">'+
					'<div class="acc-header">'+
					'<div class="heading">'+
					'<div class="value-label">disease trait</div>'+
					'<span class="label label-tag" style="background-color: '+ item.color +'" title="interesting">&nbsp;</span>'+ item.disease_trait +'</div>'+
					'<div class="row properties">'+
					'<div class="col-xs-6 col-sm-1"><div class="value-label">rsid</div>'+ (item.rsid ? item.rsid : '') +'</div>'+
					'<div class="col-xs-6 col-sm-2"><div class="value-label">chromosome position</div>'+ (item.chromosome_position ? item.chromosome_position : '') +'</div>'+
					'<div class="col-xs-6 col-sm-1"><div class="value-label">risk allele</div>'+ (item.risk_allele ? item.risk_allele : '') +'</div>'+
					'<div class="col-xs-6 col-sm-1"><div class="value-label">genotype</div>'+ (item.genotype ? item.genotype : '') +'</div>'+
					'<div class="col-xs-6 col-sm-1"><div class="value-label">p value</div>'+ (item.p_value ? item.p_value : '') +'</div>'+
					'<div class="col-xs-6 col-sm-1"><div class="value-label">or</div>'+ (item.or_or_beta ? item.or_or_beta : '') +'</div>'+
					'<div class="col-xs-6 col-sm-1"><div class="value-label">risk</div>'+ (item.risk ? item.risk : '') +'</div>'+
					'<div class="col-xs-6 col-sm-3"><div class="value-label">tags</div>'+ (item.tags ? item.tags.join(', ') : '') +'</div>'+
					'<div class="col-sm-1"><a href="#" data-url="'+ (item.link && item.risk_allele ? item.link +'?allele='+ item.risk_allele +'&ajax=1' : '') +'" class="acc-switch pull-right"><span class="on-close">more <i class="fa fa-caret-down"></i></span><span class="on-open">less <i class="fa fa-caret-up"></i></span></a></div>'+
					'</div>'+
					'</div>'+
					'<div class="acc-content"><div class="loading">Loading...</div></div>'
					+'</div>';
				}
			}

			_this.$el
				.html(html)
				.accordion();
		});
	};

	$.fn.genome = function(options) {
		return $(this).each(function(){
			new Genome(this, options);
		});
	};

})( jQuery, window, document );