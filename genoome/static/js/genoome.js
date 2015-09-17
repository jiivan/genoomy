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

$(document).ready(function() {

    var genomeData = $('#genomeData');
    genomeData.on( 'init.dt', function () {
        genomeData.fadeIn(850);
    } );
    var genomeTable = genomeData.dataTable({
        "pageLength": 50,
        "aoColumnDefs": [
            { "sType": "numeric_ignore_nan", "aTargets": [ 5, 6 ] },
            { "bSearchable": false, "bVisible": false, "aTargets": [ 8 ] }
        ],
        "order": [[ 8, "desc" ]],
        "processing": true,
        "columnDefs": [
            {
                "targets": [ 8 ],
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
        console.log(values);
        var l = values.received;
        var tot = values.size;

        var perc = (l / tot) * (100.00);
        console.log(perc);
        progressbar.css('width', perc + '%');
        if (values.status === 'done') {
            window.clearInterval(interval);
        }
    }

    $("form#upload_form").submit(function(e){
        console.log('Form submitted');
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
        var container = $('.payment-choice'),
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

    $(document).on('submit', '.payment-choice .payment-bitpay form', function(e) {
        //e.preventDefault();
        e.stopPropagation();
        purchase_data('Bitpay');
        //console.log('Bitpay submitted');
    });
    $(document).on('click', '.payment-choice .payment-coupon a', function(e) {
        //e.preventDefault();
        e.stopPropagation();
        purchase_data('Coupon');
        //console.log('Coupon submitted');
    });
    $(document).on('submit', '.payment-choice .payment-paypal form', function(e) {
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
        $("#genomeData").toggleClass($(this).val());
    });
    $("#genomeData").toggleClass('ci2');
    $("#genomeData").toggleClass('ci3');
    $("#genomeData").toggleClass('ci1');
    $('#ch4').attr('checked', true);
    $('#ch5').attr('checked', true);
    $('#ch6').attr('checked', true);
    $('#ch7').attr('checked', true);
    $('#ch8').attr('checked', true);

    $(".checkbox-lister").click(function(){
        $(".checkbox-listinn").addClass('active');


    });
    $("#savebutton").click(function(){
        $(".checkbox-listinn").removeClass('active');


    });
});
