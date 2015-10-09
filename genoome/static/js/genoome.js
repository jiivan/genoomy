$.fn.dataTableExt.oSort['numeric_ignore_nan-asc']  = function(x,y) {
    if (isNaN(x) && isNaN(y)) return ((x < y) ? 1 : ((x > y) ?  -1 : 0));

    if (isNaN(x)) return 1;
    if (isNaN(y)) return -1;

    x = parseFloat( x );
    y = parseFloat( y );
    return ((x < y) ? -1 : ((x > y) ?  1 : 0));
};

$.fn.dataTableExt.oSort['numeric_ignore_nan-desc'] = function(x,y) {
    if (isNaN(x) && isNaN(y)) return ((x < y) ? 1 : ((x > y) ?  -1 : 0));

    if (isNaN(x)) return 1;
    if (isNaN(y)) return -1;

    x = parseFloat( x );
    y = parseFloat( y );
    return ((x < y) ?  1 : ((x > y) ? -1 : 0));
};

$.fn.dataTableExt.afnFiltering.push(
    function(oSettings, aData, iDataIndex) {
        var selected_tags = $('.filter_labels span.label-warning').map(function(k, v) {
            return $(this).text();
        }).get(),
            row_tags = aData[9].split(';');

        if (!selected_tags.length) { // nothing to filter out
            return true;
        } else {
            if (!row_tags.length || (row_tags.length === 1 && row_tags[0] === "")) {
                return false;
            }
            for (var i = 0; i < selected_tags.length; i++) {
                for (var j = 0; j < row_tags.length; j++) {
                    if (selected_tags[i] === row_tags[j]) {
                        return true;
                    }
                }
            }
            return false;
        }
    }
);

$(document).ready(function() {

    var genomeData = $('#genomeData');
    genomeData.on( 'init.dt', function () {
        genomeData.fadeIn(850);
    } );
    var genomeTable = genomeData.dataTable({
        "pageLength": 50,
        "aoColumnDefs": [
            { "sType": "numeric_ignore_nan", "aTargets": [ 5, 6 ] },
            { "bSearchable": true, "bVisible": false, "aTargets": [ 8, 9 ] }
        ],
        "order": [[ 8, "desc" ]],
        "processing": true,
        "columnDefs": [
            {
                "targets": [ 8, 9 ],
                "visible": false,
                "searchable": false
            }
        ],
        "drawCallback": function( settings ) {
            var rows = $('#genomeData tbody tr');

            // Remove existing event handlers;
            rows.off('click');

            rows.click(function(e) {
                e.preventDefault();
                var row = $(this);
                window.open(row.data('url'));
            });
        }
    }).columnFilter({ sPlaceHolder: "head:after",
        aoColumns: [
            { type: "number-range" },
            { type: "number-range" },
            { type: "select" },
            { type: "select" },
            { type: "select" },
            { type: "number-range" },
            { type: "number-range" },
            { type: "number-range" },
        ]
    });
    var progressbar = $('.progress-bar');
    var interval;

    function updateBar(values) {
        //console.log(values);
        var l = values.received;
        var tot = values.size;

        var perc = (l / tot) * (100.00);
        //console.log(perc);
        progressbar.css('width', perc + '%');
        progressbar.text(perc + '%');
        if (values.status === 'done') {
            window.clearInterval(interval);
        }
    }

    $("form#upload_form").submit(function(e){
        //console.log('Form submitted');
        var getProgress = function() {
            $.ajax({
                url: "/progress",
                headers: {"X-Progress-ID": $('#progress-bar').data('upload_id')},
                dataType: 'json',
                success: function(data) {
                    updateBar(data);
                }
            });
        };
        interval = window.setInterval(getProgress, 1000);
    });

    function purchase_data(payment) {
        var container = $('.payment-choices'),
            tid = container.data('tid'),
            sku = container.data('sku');
        dataLayer.push({
            'ecommerce': {
                'purchase': {
                    'actionField': {
                        'id': tid,
                        'revenue': 19.00,
                        'option': payment
                    },
                    'products': [
                        {
                            'name': 'Genome Data Analysis',
                            'id': sku,
                        }
                    ]
                }
            }
        });
    }

    $(document).on('submit', '.payment-choices .payment-bitpay form', function(e) {
        //e.preventDefault();
        e.stopPropagation();
        purchase_data('Bitpay');
        //console.log('Bitpay submitted');
    });
    $(document).on('click', '.payment-choices .payment-coupon a', function(e) {
        //e.preventDefault();
        e.stopPropagation();
        purchase_data('Coupon');
        //console.log('Coupon submitted');
    });
    $(document).on('submit', '.payment-choices .payment-paypal form', function(e) {
        //e.preventDefault();
        e.stopPropagation();
        purchase_data('Paypal');
        //console.log('Paypal submitted');
    });

    $('div.legend').mouseenter(function(e) {
        e.preventDefault();
        $('div.legend').addClass('legend-active');
    });
	  $('div.legend').mouseleave(function(e) {
        e.preventDefault();
        $('div.legend').removeClass('legend-active');
    });

    $('.form-control input:first-child').attr("placeholder","from");
    $('.form-control input:last-child').attr("placeholder","to");

    $(".checkbox-row").change(function() {
        genomeData.toggleClass($(this).val());
    });

    $(".checkbox-lister").click(function(){
        $(".checkbox-listinn").addClass('active');
        $(document.createElement('div'))
            .addClass('modal-backdrop in')
            .appendTo($(document.body));
        $('.modal-backdrop').click(function(e) {
            $(".checkbox-listinn").removeClass('active');
            $(e.target).remove();
        });


    });
    $("#savebutton").click(function(){
        $(".checkbox-listinn").removeClass('active');
        $('.modal-backdrop').remove();
    });

    $('#defaultbutton').click(function() {
        genomeData.addClass('ci1 ci2 ci3');
        genomeData.removeClass('ci4 ci5 ci6 ci7 ci8');
        $('#ch1').attr('checked', false);
        $('#ch2').attr('checked', false);
        $('#ch3').attr('checked', false);
        $('#ch4').attr('checked', true);
        $('#ch5').attr('checked', true);
        $('#ch6').attr('checked', true);
        $('#ch7').attr('checked', true);
        $('#ch8').attr('checked', true);
    });

    $('#defaultbutton').trigger('click');

    $(document).on('reload-page', function(e) {
        location.reload();
    });

    $('.filter_labels span').on('click', function(e) {
        var label = $(e.delegateTarget);
        label.toggleClass('label-warning label-primary');
        genomeData.DataTable().draw();
    });
});
