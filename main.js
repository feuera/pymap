
head.js("dist/leaflet.js");
head.js("flot/jquery.min.js");
head.js("flot/jquery-ui.min.js");
head.js("flot/jquery.flot.min.js");
head.js("flot/jquery.flot.time.min.js");
head.js("flot/jquery.flot.resize.min.js");
head.js("flot/jquery.flot.navigate.min.js");
head.js("flot/jquery.flot.crosshair.min.js");

var map=0;
var lG;
var polyline;
var marker = 0 

head.ready(function() {
    mapInit();
    printer.text("win size: "+window.size);
});


function bindFunctions(plotDiv) {
    plotDiv.bind("plothover", function (event, pos, item) {
        gui.onGraphHover(pos.x);
         //axis coordinates for other axes, if present, are in pos.x2, pos.x3, ...
        // if you need global screen coordinates, they are pos.pageX, pos.pageY
        //if (item) {
        //    highlight(item.series, item.datapoint);
        //    printer.text("You hovered over " + pos.x + ", " + pos.y+", " +  item.datapoint);
        //}
    });
    //plotDiv.bind("plotpan", function(event, plot) {
    //});
    plotDiv.bind("plotzoom", function(event, plot) {
        //for (var x in Object.keys(plot.getYAxes())) {
        //    printer.text("obj: "+x);
        //}
        var axes = plot.getAxes();
        printer.text("zoom " + Object.keys(axes.yaxis) +" " + axes.yaxis.min + " " + axes.yaxis.max );
        axes.yaxis.zoom();
        //printer.text("a " + axes.xaxes);
    });
    plotDiv.resize(function () {
        printer.text("Placeholder is now "
            + $(this).width() + "x" + $(this).height()
            + " pixels");
    });
    $(".demo-container").resizable({
        maxWidth: 2800,
        maxHeight: 1500,
        minWidth: 450,
        minHeight: 200,
    });
}

function mapInit() {
    map = L.map('map').setView([47.15, 15.37],10);
    L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);
    lG = L.layerGroup().addTo(map);
    polyline = L.polyline([
        [47.15, 15.17],
        [47.26,15.30]
        ], {color:'red'}).addTo(map);

    map.fitBounds(polyline.getBounds());
    lG.addLayer(polyline);
    marker = L.marker(polyline.getBounds().getNorthEast()).addTo(map);
    // add an OpenStreetMap tile layer
    $("#map").resize(function(){
        map.invalidateSize(true);
        printer.text("map resize"+ map.getSize());
    });
}


function setLine(polD,col) {
    var p = L.polyline(polD,{color:col});//.addTo(map);
    map.addLayer(p);
    lG.addLayer(p);
    map.fitBounds(p.getBounds());
}

function moveMarker(ltlg) {
    marker.setLatLng(ltlg);
}

function showPlot(data, divName) {
    //printer.text("data");
    var plotDiv = $("#"+divName);
    //printer.text("plotD:"+plotDiv.length +"\n");
    if (plotDiv.length == 0) {
        $('body').append('<div class="demo-container" style="width:100%; height:200px; float:left;">\n<div id="'+ divName + '" class="demo-placeholder"></div>\n</div>');
        plotDiv = $("#"+divName);
    }
    $.plot(plotDiv, data ,{
        xaxis: { mode: "time", timeformat: "%H:%M:%S", zoomRange: [1], }, 
        yaxis: { zoomRange: false },
        crosshair: { mode: "x" },
        grid: { hoverable: true, autoHighlight: false },
        zoom: { interactive: true },
        pan: { interactive: true },
    });
    bindFunctions(plotDiv);
}

function clearMap() {
    lG.clearLayers();
    //for (p in polys) {
    //    map.removeLayer(polys.pop());
    //}
}

