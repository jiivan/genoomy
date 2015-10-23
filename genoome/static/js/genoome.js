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
        var selected_tags = $('.filter_labels h3 span.tag-checked').map(function(k, v) {
                return $(this).text();
            }).get(),
            row_tags = aData[9].split(';');
        console.log(selected_tags);

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


var genomeData = $('#genomeData');
$(document).ready(function() {
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
            { type: "select" },
            { type: "number-range" },
            { type: "select" }
        ]
    });

});

$('.genomeData_advanced').click(function(e) {
    $('#genomeData thead tr.filter-visiblity, .dataTables_length, .dataTables_filter, .table-settings').toggle();
});

$(".checkbox-row input").change(function() {
    var checked = $(this).is(":checked");
    var index = $(this).parent().parent().index();
    $('#genomeData tbody tr').each(function() {
        if(checked) {
            $(this).find("td").eq(index).show();
        } else {
            $(this).find("td").eq(index).hide();
        }
    });
    $('#genomeData thead tr').each(function() {
        if(checked) {
            $(this).find("th").eq(index).show();
        } else {
            $(this).find("th").eq(index).hide();
        }
    });
    $('#genomeData tfoot tr').each(function() {
        if(checked) {
            $(this).find("th").eq(index).show();
        } else {
            $(this).find("th").eq(index).hide();
        }
    });
});

$(document).ready(function() {
    $(".checkbox-row input").trigger('change');
});

$('.filter_labels h3 span.label').on('click', function(e) {
    var label = $(e.delegateTarget);
    label.toggleClass('tag-checked');
    label.
    genomeData.DataTable().draw();
});