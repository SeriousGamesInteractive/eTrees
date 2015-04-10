"use strict";


var csrftoken;
/**

TEMPLATES FOR THE PAGE

**/

var templateUsers =	'<br><h3>Story name: {{story_name}}</h3>\
					<h4> List of users:</h4>\
					<div class="col-lg-3 col-md-3 col-sm-3">\
						<input class="search" placeholder="Search user"/>\
						<fieldset class="list-users well">\
							<div id="hacker-list">\
								<ul class="list">\
								{{#each users}}\
									<li><a href="#" id="project-{{id}}" class="user-story">{{username}}</a></li>\
									<div id="session_container-{{id}}" class="session_container" style="display:none">\
										<ul>\
										{{#each sessions}}\
											<li><a href="#" class="session-element" id="session-{{id}}">Session {{@index}} </a></li>\
											<div class="session-category" style="display:none">\
												<ul>\
												{{#each ../categories}}\
													<li><a href="#" class="category-element">{{name}}</a></li>\
												{{/each}}\
												</ul>\
											</div>\
										{{/each}}\
										</ul>\
									</div>\
								{{/each}}\
								</ul>\
							</div>\
						</fieldset>\
					</div>\
					<div class="col-lg-9 col-md-9 col-sm-9" id="report-container">\
					</div>';

var templateSession = 	'<div id="table-container">\
							<h4>Number of questions: {{number_question}}</h4>\
							<table class="table table-hover">\
							<thead>\
								<tr>\
									<th> #</th>\
									<th >Node name</th>\
									<th colspan=3>{{category.name}}</th>\
								</tr>\
								<tr>\
									<th colspan=2></th>\
									<th>max score</th>\
									<th>min score</th>\
									<th>actual score</th>\
								</tr>\
							</thead>\
							<tbody>\
								{{#each session}}\
									<tr>\
										<td>Q{{plusOne @index}}</td>\
										<td>{{node_name}}</td>\
										<td>{{maxvalue}}</td>\
										<td>{{minvalue}}</td>\
										<td>{{category_value}}</td>\
									<tr>\
								{{/each}}\
							</tbody>\
						</table>\
						</div>\
						<div >\
							{{#times numberChar}}\
								<svg class="chart-{{this}}"></svg>\
							{{/times}}\
						</div>';

var sessionSelected = null;
/**
INIT THE CONTROL OF THE PAGE WITH JQUERY
**/
$(document).ready(function(){
	csrftoken= getCookie('csrftoken');
	$(".box-unfinish").unbind("click");

	$(".box-unfinish").bind("click",function(){

		requestUserStory($(this).attr('id').split("-")[1]);

		$("#story-view").fadeOut("slow");
	});
});


/**
	FUNCTIONS 
**/

function requestUserStory(storyId) {
	var rootURL = window.location.origin;
	$.ajax({
		type: 'POST'	,
		url: rootURL+"/api/requestCompleteStoryUsers/",//To reach the api url
		data:{'storyid':storyId},
		async:false,
		beforeSend: function(xhr, settings) {
		    if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
		        // Send the token to same-origin, relative URLs only.
		        // Send the token only if the method warrants CSRF protection
		        // Using the CSRFToken value acquired earlier
		        xhr.setRequestHeader("X-CSRFToken", csrftoken);
		    }
		},
		success: function(msg) {
			if (msg.status == 'ok') {
				var compiledTemplate = Handlebars.compile(templateUsers);
				var html = compiledTemplate(msg);
				console.log(msg)
				$("#container").html(html);
				handleListUsers();
			} else {
				$.error("Message:" +msg.error)
			}
				  
		},
		error: function (thrownError) {
		    $.error(thrownError);
		}
	});

}


function handleListUsers() {
	$(".user-story").click(function() {
		$(".session_container").hide();
		$('.session-category').hide();
		$("#session_container-" + $(this).attr('id').split("-")[1]).fadeIn("slow");
	});
	var options = {
		valueNames: ['user-story']
	};
	//List control the search functionlity on the list
	var userList = new List('hacker-list', options);
	$(".search").unbind('keyup keydown');
	$(".search").bind('keyup keydown',function(e) {
		
		userList.search($(this).val());
	});
	$('.session-element').unbind('click');
	$(".session-element").bind('click',function(){		
		$('.session-category').fadeOut("slow");
		$(this).parent().next('.session-category').fadeIn("slow");
		getSessionData($(this).attr('id').split("-")[1])
	});

	$('.category-element').unbind('click');
	$(".category-element").bind('click', function(){
		showGraphics($(this).html());
	});

}

/**
*
* Request the session data of the game, getting the information of the categories and the node selected
*/
function getSessionData(sessionId) {

	var rootURL = window.location.origin;
	$.ajax({
		type: 'POST'	,
		url: rootURL+"/api/requestSessionGameUsers/",//To reach the api url
		data:{'sessionId':sessionId},
		async:false,
		beforeSend: function(xhr, settings) {
		    if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
		        // Send the token to same-origin, relative URLs only.
		        // Send the token only if the method warrants CSRF protection
		        // Using the CSRFToken value acquired earlier
		        xhr.setRequestHeader("X-CSRFToken", csrftoken);
		    }
		},
		success: function(msg) {
			if (msg.status == 'ok') {
				sessionSelected = msg;
			
				console.log(msg);
			} else {
				$.error("Message:" +msg.error)
			}
				  
		},
		error: function (thrownError) {
		    $.error(thrownError);
		}
	});

	return;
}

function showGraphics(categoryName) {
	console.log("Sessionselected ",sessionSelected);
	var bindingJson = {"category":{"name":categoryName}};
	bindingJson["session"] = [];
	var chartJson = [];
	for (var i = 0; i < sessionSelected.session.length; i++) {	
		var node = sessionSelected.session[i];
		var categoryItem = _.findWhere(node.categories,{"name":categoryName});
		
		var range = _.findWhere(node.categoryRange,{"name":categoryName});
		var minValue = 0;
		var maxValue = 0;
		if (range !== undefined){
			minValue = parseInt(range.minvalue);
			maxValue = parseInt(range.maxvalue);
		}
		var template = {"node_id":node.node_id, "node_name":node.node_name,
		"option_name":node.option_name,"category_value":categoryItem !== undefined ? categoryItem.value:0,
		"maxvalue":maxValue,"minvalue":minValue};
		chartJson.push({"name":"Q" + (i+1),"maxvalue": parseInt(maxValue),"minvalue":parseInt(minValue), 
		"value":categoryItem !== undefined ? categoryItem.value:0}); 
		bindingJson["session"].push(template);


	}
	//HELPER for handlebars
	Handlebars.registerHelper('plusOne', function(value){
    	return parseInt(value) + 1; //I needed human readable index, not zero based
	});
	Handlebars.registerHelper('times', function(n, block) {
	    var accum = '';
	    for(var i = 1; i <= n; ++i)
	        accum += block.fn(i);
	    return accum;
	});

	bindingJson["number_question"] = i;
	var compiledTemplate = Handlebars.compile(templateSession);
	//Implementation of several charts depending on the numbers of nodes
	//MAx number of node per chart 30
	
	//Remove from the grafh the last node, because it is the end node and it does not have relevant data
	chartJson.pop();
	var numberChars = (Math.floor(chartJson.length / 30) + 1);

	bindingJson['numberChar']  = numberChars;
	var html = compiledTemplate(bindingJson);
	

	$("#report-container").html(html);
	for (var i = 1; i <= numberChars; i++) {
		showChart("chart-"+i,chartJson.slice(0 +(30 * (i-1)), 30 +(30 * (i-1)) ));
	}
	//showChart(resultJson);
	//showChart(chartJson);

}


