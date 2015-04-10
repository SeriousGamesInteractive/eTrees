var csrftoken;
$(document).ready(function(){
	"use strict";
	csrftoken= getCookie('csrftoken');


	$('.icon-delete').mouseover(function(){
		$(this).parent().parent().bind('click',false);
	});
	$('.icon-delete').mouseout(function(){
		$(this).parent().parent().unbind('click',false);
	});
	$('.icon-delete').bind('click',function(){
		//$(this).parent().parent().unbind('click',false);
		var answer = confirm("Do you want to delete the story"+$(this).parent().text().replace(/\s+/g, ' ') +" ? "+
			"\n (Only if the story has not been assigned to an user)");
		if (answer) { 

			deleteStory($(this).children("i").attr("id").split('-')[1]);
			
		}
	});

});

/**
* Delete node providing the id of the story.
* Make a AJAX request.
*/
function deleteStory(id){
	console.log("The id", id);
	$.ajax({
		type: 'POST'	,
		url: document.location.origin + "/api/requestDeletePublishStory/",
		data: {'storyid':id},
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
			//Remove the node in the list. <div><a><button><i></i></button></a></div>
			if(msg.status == "ok") {   
				$("#deletenode-"+id).parent().parent().empty();
			} else if (msg.status == "permissions"){
				$("#temp-message-error").html(msg.message);
			}else {
				$("#temp-message-error").html(msg.error);
			}
		},
		error: function (thrownError) {
		    $.error(thrownError);
		}
	});
	
}



