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
		url: 'data/genome-data.json',
		counterText: 'Showing %1 to %2 of %3 entries'
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

		_this.pagination = {
			$el: $(_this.options.pagination)
		};
		_this.$counter = $(_this.options.counter);
		_this.$perPage = $(_this.options.perPage);
		_this.scrollOffset = $('.navbar-fixed-top').outerHeight() + 10;

		_this.page = 0;
		_this.perPage = 10;

		$.getJSON(_this.options.url, function(data) {
			if (data) {
				_this.buildList(data.data);
				_this.updateCounter();
				_this.buildPagination();
			}
		});

		_this.pagination.$el
			.on('click', 'li', function(e) {
				e.preventDefault();
				var $this = $(this);

				if ($this.hasClass('disabled'))
					return false;

				if ($this.hasClass('prev')) {
					_this.page--;
				} else if ($this.hasClass('next')){
					_this.page++;
				} else {
					_this.page = $(this).data('page');
				}

				_this.updateList();
				_this.updatePagination();
				_this.updateCounter();
			});

		_this.$perPage.on('change', function(){
			_this.perPage = _this.$perPage.val();
			_this.page = 1;
			_this.updateList();
			_this.buildPagination();
			_this.updateCounter();
		});
	};

	Genome.prototype.buildList = function(data) {
		var _this = this;
		var html = '';

		for (var i in data) {
			if (data.hasOwnProperty(i)) {
				var item = data[i];

				html += '<div class="acc'+ (i >= _this.perPage ? ' off-page' : '') +'">'+
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
				'<div class="col-sm-1"><a href="#" data-url="'+ (item.link ? item.link : '') +'" class="acc-switch pull-right"><span class="on-close">more <i class="fa fa-caret-down"></i></span><span class="on-open">less <i class="fa fa-caret-up"></i></span></a></div>'+
				'</div>'+
				'</div>'+
				'<div class="acc-content"></div>'
				+'</div>';
			}
		}

		_this.$el
			.html(html)
			.accordion();

		_this.page = 0;
		_this.total = data.length;

		_this.$items = _this.$el.find('.acc');
		_this.$visible = _this.$items.not('.hidden');
	};

	Genome.prototype.buildPagination = function() {
		var _this = this,
			html = '<li class="prev disabled"><a href="#" aria-controls="genome-listing" tabindex="0">Previous</a></li>';

		_this.maxPage = Math.ceil(_this.total / _this.perPage);

		for (var i = 0; i < _this.maxPage; i++) {
			html += '<li class="page page-'+ i +' '+ (i === 0 ? ' active' : '') +'" data-page="'+ i +'"><a href="#" class="" aria-controls="genome-listing" tabindex="0">'+ (i+1) +'</a></li>';
		}

		html += '<li class="next'+ (_this.maxPage === 1 ? ' disabled' : '') +'"><a href="#" aria-controls="genome-listing" tabindex="0">Next</a></li>';

		_this.pagination.$el.html(html);
		_this.pagination.$prev = _this.pagination.$el.find('.prev');
		_this.pagination.$next = _this.pagination.$el.find('.next');
	};

	Genome.prototype.updateList = function() {
		var _this = this;

		_this.$items.addClass('off-page')
			.slice(_this.page * _this.perPage, (_this.page+1) * _this.perPage).removeClass('off-page');

		$('html, body').animate({
			scrollTop: _this.$el.offset().top - _this.scrollOffset
		}, 300);
	};

	Genome.prototype.updatePagination = function() {
		var _this = this;

		_this.pagination.$el.find('.active').removeClass('active');
		_this.pagination.$el.find('.page-'+ _this.page).addClass('active');

		_this.pagination.$prev.toggleClass('disabled', _this.page == 0);
		_this.pagination.$next.toggleClass('disabled', _this.page == _this.maxPage-1);
	};

	Genome.prototype.updateCounter = function() {
		var _this = this,
			text = _this.options.counterText;

		text = text.replace('%1', _this.page * _this.perPage + 1);
		text = text.replace('%2', (_this.page+1) * _this.perPage);
		text = text.replace('%3', _this.$visible.length);

		_this.$counter.html(text);
	};

	$.fn.genome = function(options) {
		return $(this).each(function(){
			new Genome(this, options);
		});
	};

})( jQuery, window, document );