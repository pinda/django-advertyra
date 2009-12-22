// All the functions and basic vars for plotting the graphs

var options = {
    xaxis: { mode: "time" },
    yaxis: { min: 0 },
    grid: { markings: weekendAreas },
    lines: { show: true },
    points: { show: true }
};

function plotSingle(data, extras){
    $('#placeholder').empty();
    var d = data;
    $.extend(true, options, extras);

    // first correct the timestamps - they are recorded as the daily
    // midnights in UTC+0100, but Flot always displays dates in UTC
    // so we have to add one hour to hit the midnights in the plot
    for (var i = 0; i < d.length; ++i)
      d[i][0] += 60 * 60 * 1000;

    var plot = $.plot($("#placeholder"), [d], options);
}

function plotMulti(datasets, extras){
    $('#placeholder').empty();

    var data = [];
    var choiceContainer = $('#choices');

    $.extend(true, options, extras);
    choiceContainer.find("input:checked").each(function () {
        var key = $(this).attr("name");
        if (key && datasets[key])
            data.push(datasets[key]);
        });
        
    if (data.length > 0)
        $.plot($("#placeholder"), data, options);
}

function prepareData(datasets){
    var choiceContainer = $('#choices');
    choiceContainer.empty();

    var i = 0;
    $.each(datasets, function(key, val) {
        val.color = i;
        ++i;
    });
    
    // insert checkboxes 
    $.each(datasets, function(key, val) {
        choiceContainer.append('<li><input type="checkbox" name="' + key +
                               '" checked="checked" id="id' + key + '">' +
                               '<label for="id' + key + '">'
                               + val.label + '</label></li>');
    });

    choiceContainer.find("input").click(function(){
        plotMulti(datasets);
    });

}

// helper for returning the weekends in a period
function weekendAreas(axes) {
    var markings = [];
    var d = new Date(axes.xaxis.min);
    // go to the first Saturday
    d.setUTCDate(d.getUTCDate() - ((d.getUTCDay() + 1) % 7))
    d.setUTCSeconds(0);
    d.setUTCMinutes(0);
    d.setUTCHours(0);
    var i = d.getTime();
    do {
        // when we don't set yaxis, the rectangle automatically
        // extends to infinity upwards and downwards
        markings.push({ xaxis: { from: i, to: i + 2 * 24 * 60 * 60 * 1000 } });
        i += 7 * 24 * 60 * 60 * 1000;
    } while (i < axes.xaxis.max);

    return markings;
}