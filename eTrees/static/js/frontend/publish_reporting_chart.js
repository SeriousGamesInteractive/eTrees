/************************************************************************

 D3.js implementation

*************************************************************************/

function showChart(nameChart,data) {

	console.log("DATA: ",data)
	/*
	data = [
		{name: "Locke",    value:  4},
        {name: "Reyes",    value:  8},
        {name: "Ford",     value: 15},
        {name: "Jarrah",   value: 16},
        {name: "Shephard", value: 23},
        {name: "Kwon",     value: 42}
	];
	*/
	var margin = {top: 30, right: 10, bottom: 30, left: 30},
        width = 800 - margin.left - margin.right,
        height = 350 - margin.top - margin.bottom;

	var x = d3.scale.ordinal()
        .rangeRoundBands([0, width],0.2);

	var y = d3.scale.linear()
        .range([height,0]);

	var xAxis = d3.svg.axis()
        .scale(x)
        .orient("bottom");

	
	var yAxis = d3.svg.axis()
		.scale(y)
		.orient("left");
	
	var svg = d3.select("."+nameChart)
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)   
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

	var dataMinMax = [
		{value: _.min(data, function(data){ return data.minvalue; }).minvalue},
		{value: _.max(data, function(data){ return data.maxvalue; }).maxvalue}
		];

	x.domain(data.map(function(d) { return d.name; }));
	y.domain(d3.extent(dataMinMax, function(d) { return d.value; }));
    //y.domain(data.extend);
    
    
	svg.selectAll(".bar")
        .data(data)
        .enter().append("rect")
        .attr("class", function(d) { return d.value < 0 ? "bar negative" : "bar positive"; })
        .attr("x", function(d) { console.log("x name " + d.name,x(d.name)); return x(d.name); })
        .attr("y", function(d) { console.log("y ",y(Math.min(0, d.maxvalue))); return  y(Math.max(0, d.maxvalue));})
        .attr("width",  x.rangeBand())
        .attr("height", function(d) { console.log("value here: ",Math.abs(y(d.value) - y(0)));return  Math.abs(y(d.maxvalue) - y(d.minvalue));});//.attr("height", function(d) { return y(d.value) ;});
            
    svg.selectAll(".dot")
      .data(data)
    .enter().append("circle")
      .attr("class", "dot")
      .attr("r", 6)
      .attr("cx", function(d) { return x(d.name) + (x.rangeBand() / 2); })
      .attr("cy", function(d) { return  y(d.value); })
      .style("fill", function(d) { return "#FFFF00"; });
        
	
	svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis);
    
	svg.append("g")
		.attr("class", "y axis")
		.call(yAxis);
	
	svg.append("g")
        .attr("class", "x axis")
        .append("line")
        .attr("y1", y(0))
        .attr("y2", y(0))
        .attr("x2", width);
}

function showChart_old(data) {

	console.log("DATA: ",data)
	/*
	data = [
		{name: "Locke",    value:  4},
  		{name: "Reyes",    value:  8},
  		{name: "Ford",     value: 15},
  		{name: "Jarrah",   value: 16},
  		{name: "Shephard", value: 23},
  		{name: "Kwon",     value: 42}
	];
	*/
	var margin = {top: 30, right: 10, bottom: 30, left: 30},
	    width = 800 - margin.left - margin.right,
	    height = 350 - margin.top - margin.bottom;

	var x = d3.scale.ordinal()
	    .rangeRoundBands([0, width],.2)

	var y = d3.scale.linear()
	    .range([height,0]);

	var xAxis = d3.svg.axis()
	    .scale(x)
	    .orient("bottom");

	
	var yAxis = d3.svg.axis()
		.scale(y)
		.orient("left");
	
	var svg = d3.select(".chart")
	    .attr("width", width + margin.left + margin.right)
	    .attr("height", height + margin.top + margin.bottom)
	  	.append("g")
	    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

	var dataMinMax = [
		{value:data[0].minvalue},
		{value:data[0].maxvalue}
		];

	x.domain(data.map(function(d) { return d.name; }));
	y.domain(d3.extent(dataMinMax, function(d) { return d.value; }));

	svg.selectAll(".bar")
	    .data(data)
		.enter().append("rect")
	    .attr("class", function(d) { return d.value < 0 ? "bar negative" : "bar positive"; })
	    .attr("x", function(d) { return x(d.name); })
	    .attr("y", function(d) { return y(Math.max(d.value,0));  })
	    .attr("width",  x.rangeBand())
	    .attr("height", function(d) { return Math.abs(y(d.value) - y(0));});
	/*
	  svg.append("circle")
      .attr("r", function(d) { return d.r; })
      .style("fill", function(d) { return color(d.packageName); });
	*/
	svg.append("g")
	    .attr("class", "x axis")
	    .attr("transform", "translate(0," + height + ")")
	    .call(xAxis);
	    
	svg.append("g")
		.attr("class", "y axis")
		.call(yAxis);
	
	svg.append("g")
	    .attr("class", "x axis")
		.append("line")
	    .attr("y1", y(0))
	    .attr("y2", y(0))
	    .attr("x2", width);

	   /*
	svg.append("g")
		.attr("class","y axisname")
		.call(yAxis)
		.append("text")
    	.attr("transform", "rotate(-90)")
    	.attr("y", -6)
    	.attr("dy", ".71em")
    	.style("text-anchor", "end")
    	.text("Nodes");
	*/
}

