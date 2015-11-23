$.cssHooks.backgroundColor = {
    get: function(elem) {
        if (elem.currentStyle)
            var bg = elem.currentStyle["backgroundColor"];
        else if (window.getComputedStyle)
            var bg = document.defaultView.getComputedStyle(elem,
                null).getPropertyValue("background-color");
        if (bg.search("rgb") == -1)
            return bg;
        else {
            bg = bg.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/);
            function hex(x) {
                return ("0" + parseInt(x).toString(16)).slice(-2);
            }
            return "#" + hex(bg[1]) + hex(bg[2]) + hex(bg[3]);
        }
    }
};

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

$.fn.dataTableExt.afnFiltering.push(
    function(oSettings, aData, iDataIndex) {
        var selected_categories = $('.category_labels h2 span.tag-checked').map(function(k, v) {
                return $(this).css('background-color');
            }).get(),
            row_color = aData[10];
        if (!selected_categories.length) { // nothing to filter out
            return true;
        } else {
            for (var i = 0; i < selected_categories.length; i++) {
                if (selected_categories[i] === row_color) {
                    return true;
                }
            }
        }
        return false;
    }
);

var genomeData = $('#genomeData');
$(document).ready(function() {
    var genome_url = genomeData.data('genome_url');
    var genomeTable = genomeData.dataTable({
        "ajax": genome_url,
        "columns": [
            {"data": "rsid" },
            {"data": "chromosome_position" },
            {"data": "risk_allele" },
            {"data": "genotype" },
            {"data": "disease_trait" },
            {"data": "p_value" },
            {"data": "or_or_beta" },
            {"data": "risk" },
            {"data": "priority", "defaultContent": "0" },
            {"data": "tags", "defaultContent": ""},
            {"data": "color", "defaultContent": ""}
        ],
        "pageLength": 100,
        "aoColumnDefs": [
            { "sType": "numeric_ignore_nan", "aTargets": [ 5, 6 ] },
            { "bSearchable": false, "bVisible": false, "aTargets": [ 8 ] }
        ],
        "columnDefs": [{"targets": [ 8 ], "visible": false, "searchable": false}],
        "order": [[ 8, "desc" ]],
        "processing": true,
        "drawCallback": function( settings ) {
            var rows = $('#genomeData tbody tr');

            // Remove existing event handlers;
            rows.off('click');

            rows.click(function(e) {
                e.preventDefault();
                var row = $(this);
                window.open(row.data('url'));
            });
            // Fix datatable for fluid container
            genomeData.css('width', '');

            // Ugly way to make table columns show/hide on init as requested
            var checkbox_settings = [
                false, // RSID
                false, // CHROMOSOME POS
                false, // RISK ALLELE
                true, // GENOTYPE
                true, // DISEASE TRAIT
                true, // P VALUE
                true, // OR
                true, // RISK
                false, // PRIORITY
                false, // TAGS
                false  // CATEGORY COLOR
            ];
            var checkboxes = $(".checkbox-row input");
            checkbox_settings.forEach(function(element, index) {
                var checkbox = $(checkboxes[index]);
                checkbox.trigger('change')
                    .attr('checked', element);
            });

            rowRender()
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

    function rowRender() {
        $('#genomeData').DataTable().rows().every(function() {
            var row = $(this.node()),
                rowData = this.data();
            row.data('url', encodeURI(rowData.link + '?allele=' + rowData.genotype))
                .css('background-color', rowData.color);
        });
    }

});


var progressbar = $('.progress-bar');
var interval;

function updateBar(values) {
    var l = values.received;
    var tot = values.size;

    var perc = (l / tot) * (100.00);
    progressbar.css('width', perc + '%');
    progressbar.text(perc + '%');
    if (values.status === 'done') {
        window.clearInterval(interval);
    }
}

$("form#upload_form").submit(function(e){
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


$('.filter_labels h3 span.label').on('click', function(e) {
    var label = $(e.delegateTarget),
        labelColorOff = label.data('color-off'),
        labelColorOn = label.data('color-on');
    label.toggleClass('tag-checked');
    if (label.hasClass('tag-checked')) {
        label.css('background-color', labelColorOn);
    } else {
        label.css('background-color', labelColorOff);
    }
    genomeData.DataTable().draw();
});

$('.category_labels h2 span.label').on('click', function(e) {
    var category = $(e.delegateTarget);
    category.toggleClass('tag-checked');
    genomeData.DataTable().draw();
});

/**
 * Layout expand
 */
function setLayout() {
    if(window.localStorage['expand'] == 'true') {
        $('.layout').removeClass('container container-fluid').addClass('container-fluid')
        $('[data-toggle=layout-fluid] .glyphicon.glyphicon-resize-full').removeClass('glyphicon-resize-full').addClass('glyphicon-resize-small')
    } else {
        $('.layout').removeClass('container container-fluid').addClass('container')
        $('[data-toggle=layout-fluid] .glyphicon.glyphicon-resize-small').removeClass('glyphicon-resize-small').addClass('glyphicon-resize-full')
    }
}

//setLayout();

$('[data-toggle=layout-fluid]').click(function() {
    window.localStorage['expand'] = String(!(window.localStorage['expand'] == 'true'));
    setLayout();
    return false;
});


if (window.location.href === '/disease/browse/') {
    (function poll(){
        setTimeout(function(){
            if ($('.alert.alert-info').length) {
                location.reload();
                poll();
            }
        }, 1000);
    })();
}

