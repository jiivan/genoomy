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
    var genomeTable = genomeData.dataTable({
        "pageLength": 100,
        "aoColumnDefs": [
            { "sType": "numeric_ignore_nan", "aTargets": [ 5, 6 ] }
        ],
        "order": [[ 8, "desc" ]],
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
            { type: "select" }
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
            headers: {"X-Progress-ID": "{{ upload_id }}"},
            dataType: 'json',
            success: function(data) {
                updateBar(data);
            }
        });
    };
    interval = window.setInterval(getProgress, 1000);
});


});