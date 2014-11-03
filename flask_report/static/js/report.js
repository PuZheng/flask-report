$.extend($.fn.dataTableExt.oStdClasses, {
    "sWrapper": "dataTables_wrapper form"
});

$(function () {
    $('#report a[data-role="drill-down-link"]').click(
        function () {
        var modal = $('#drill-down-detail');
        modal.find('.modal-header h3').text(sprintf('{{ _("detail of %%s") }}', $(this).attr('data-col')));
        modal.modal('show');
        var content = modal.find('.modal-body p');
        content.html('<i class="fa fa-refresh fa-4x"></i>');
        content.load($(this).attr('data-target'), function (response, status, xhr) {
            if (status != "success") {
            $(this).html($("<p></p>").text("{{ _("Load Error") }}").addClass("text-error"));
            }
        });
        });
    var sum_columns = {{ report.sum_column_index }};
    var sumsCallback = function (nRow, aaData, iStart, iEnd, aiDisplay) {
    var sums = [];
    for (i = iStart; i < iEnd; i++) {
        for (j = 0; j < aaData[aiDisplay[i]].length; j++) {
        var num = parseFloat(aaData[aiDisplay[i]][j]);
        if (!isNaN(num)) {
            if (sums[j]) {
            sums[j] += num;
            } else {
            sums[j] = num;
            }
        }
        }
    }
    for (var i = 0; i < sums.length; i++) {
        var visibleIndex = this.fnSettings().oApi._fnColumnIndexToVisible(this.fnSettings(), i);
        if (visibleIndex != null && ( sum_columns.length == 0 || $.inArray(visibleIndex, sum_columns) > -1)) {
        if (sums[i]) {
            $('#report tfoot th:eq(' + visibleIndex + ')').html('<b>' + '{{ _("Total") }}' + ': ' + sums[i] + '</b>');
        } else {
            $('#report tfoot th:eq(' + visibleIndex + ')').html('');
        }
        }
    }
    }

    function parse(str) {
    str = $.trim(str);
    if (!isNaN(str)) {
        str = Number(str);
    }
    return str;
    }

    jQuery.fn.dataTableExt.oSort['html-asc'] = function (x, y) {
    x = parse(x);
    y = parse(y);
    return ((x < y) ? -1 : ((x > y) ? 1 : 0));
    };

    jQuery.fn.dataTableExt.oSort['html-desc'] = function (x, y) {
    x = parse(x);
    y = parse(y);
    return ((x < y) ? 1 : ((x > y) ? -1 : 0));
    };

    var oTable = $("#report").dataTable({
    "oLanguage": {
        "sLengthMenu": '{{ _("Display _MENU_ records per page") }}',
        "sZeroRecords": '{{ _("Nothing found - sorry") }}',
        "sInfo": '{{ _("Showing _START_ to _END_ of _TOTAL_ records") }}',
        "sInfoEmpty": '{{ _("Showing 0 to 0 of 0 records") }}',
        "sInfoFiltered": "(" + '{{ _("filtered from _MAX_ total records") }}' + ")",
        'oPaginate': {
        "sPrevious": '{{ _("Previous") }} ',
        "sNext": '{{ _("Next") }}',
        "sFirst": '{{ _("First") }}',
        'sLast': '{{ _("Last") }}'
        }
    },
    "bSortCellsTop": true,
    "sDom": "<'row'<'col-lg-6'l>r>t<'row'<'col-lg-6'i><'col-lg-6'p>>",
    "iDisplayLength": 25,
    "fnFooterCallback": sumsCallback
    });

    $("#detail").on('shown', function () {
    $('a[data-target="#detail"]').text("{{ _('hide detail') }}" + " <<");
    });
    $("#detail").on('hidden', function () {
    $('a[data-target="#detail"]').text("{{ _('show detail') }}" + " >>");
    });


    /* Add the events etc before DataTables hides a column */
    $("thead input").keyup(function () {
    /* Filter on the column (the index) of this element */
    oTable.fnFilter(this.value, oTable.oApi._fnVisibleToColumnIndex(
        oTable.fnSettings(), $("thead input").index(this)));
    });

    /*
    * Support functions to provide a little bit of 'user friendlyness' to the textboxes
    */
    $("thead input").each(function (i) {
    this.initVal = this.value;
    });

    $("thead input").focus(function () {
    if (this.className == "search_init") {
        this.className = "";
        this.value = "";
    }
    });

    $("thead input").blur(function (i) {
    if (this.value == "") {
        this.className = "search_init";
        this.value = this.initVal;
    }
    });

});
