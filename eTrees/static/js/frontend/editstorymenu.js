var csrftoken;
$(document).ready(function(){
	"use strict";
	csrftoken= getCookie('csrftoken');


	$('.icon-copy').mouseover(function(){
		$(this).parent().parent().bind('click',false);
	});
	$('.icon-copy').mouseout(function(){
		$(this).parent().parent().unbind('click',false);
	});
	$('.icon-copy').bind('click',function(){
		$(this).parent().parent().unbind('click',false);
		var answer = confirm("Do you want to create a new copy of the story "+$(this).parent().text().replace(/\s+/g, ' ') +" ? "+
			"\n (You can edit the name and categories)");
		if (answer) { 

			var root = window.location.origin; 
			window.location.replace(root+"/project/copy-story/"+$(this).children().attr("id").split("-")[1]) ;
			
		}
	});

});



