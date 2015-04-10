$(document).ready(function(){
	csrftoken= getCookie('csrftoken');
	if(!$('.warning-message').is(':empty')){
		$('#newstoryModal').modal('show');
	};
	//Check if initial node exist or not
	var listTypeNode = $('.node-type');
	var flagInit = false;
	var flagEnd = false;
	for (var i = 0; i < listTypeNode.length; i++){
		if (listTypeNode[i].value==1){// Node type initial
			flagInit = true;
		}
		if (listTypeNode[i].value ==2){
			flagEnd = true;
		}
	}

	if (flagInit){
		$('#initial-node-section').hide();
	}
	/*
	if (flagInit && flagEnd){
		$("#tree_connection_auxbutton").hide();
	} else {
		$("#tree_connection_button").hide();
	}
	*/
	//Feedback user when the initial or ending node are not created
	$("#tree_connection_auxbutton").click(function(){
		$("#temp-message").fadeIn("fast",
			function(){$("#temp-message").html("Node initial and ending have to be created to start the tree tool");});
		$("#temp-message").fadeOut(5000);
	});

	$('.icon-delete').mouseover(function(){
		$(this).parent().parent().bind('click',false);
	});
	$('.icon-delete').mouseout(function(){
		$(this).parent().parent().unbind('click',false);
	});
	$('.icon-delete').bind('click',function(){
		$(this).parent().parent().unbind('click',false);
		var answer = confirm("Do you want to delete the node"+$(this).parent().text().replace(/\s+/g, ' ') +" ? "+
			"\n (You will also delete the connection created to this node)");
		if (answer) { 
			deleteNode($(this).children("i").attr("id").split('-')[1]);
		}
	});


	$('.icon-nodecopy').mouseover(function(){
		$(this).parent().parent().bind('click',false);
	});
	$('.icon-nodecopy').mouseout(function(){
		$(this).parent().parent().unbind('click',false);
	});
	$('.icon-nodecopy').bind('click',function(){
		$(this).parent().parent().unbind('click',false);
		var typeNode = $(this).children("i").attr("id").split('-')[2];
		if(typeNode == 1) {
			alert("A initial node cannot be duplicated.");
			return;
		}
		var idNode = $(this).children("i").attr("id").split('-')[1];
		$("#confirm-copynode-modal").modal("show");
		$("#yes-copynode").unbind('click');
		$("#yes-copynode").bind('click', function() {
			var nameNode = $("#copy-node-name").val();
			if (nameNode.length === 0) {

				alert("You have to enter a name for the node");
				return;
			}
			copyNode(idNode,nameNode);
		});
		/*
		var answer = confirm("Do you want to copy this node"+$(this).parent().text().replace(/\s+/g, ' ') +" ? ");
		if (answer) { 
			copyNode($(this).children("i").attr("id").split('-')[1]);
		}
		*/
	});

	$('.icon-node-edit').mouseover(function(){
		$(this).parent().parent().bind('click',false);
	});
	$('.icon-node-edit').mouseout(function(){
		$(this).parent().parent().unbind('click',false);
	});
	$('.icon-node-edit').bind('click',function(){
		$(this).parent().parent().unbind('click',false);
		var idNode = $(this).children("i").attr("id").split('-')[1];
		$.ajax({
			type: 'POST'	,
			url: "/api/requestNodeData/",
			data:{"nodes":[idNode]},
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
				var node = msg.nodes[0]; //Get the node info
				$("#editInputName").val(node.name);
				$("#editInputDescription").val(node.description);
				$("#editNodeId").val(node.id);
				$("#editNodeModal").modal("show");
			},
			error: function (thrownError) {
			    $.error(thrownError);
			}
		
		});
	});

	var rootUrl = window.location.origin;
	$.each($(".box-unfinish"),function(index,value){
		var nodeid = $(value).attr("id").split("-")[1];
		var storyid = $("#story-id").val();
		var nc = new Date();
		nc = nc.getTime();
		$(value).css("background-image",'url('+rootUrl+'/media/stories/'+storyid+'/screenshot'+nodeid+'.jpg?nc='+nc+')');
		$(value).css("background-size","cover");
	});
	$("#temp-message").fadeOut(3000);
	//Publish story button to confirm 
	$("#yes-publish").click(function(){
		if ($("#publish-story-name").val() == "") {
			alert("You have to enter a name for the story");
			return;
		}
		publishStory($(this).val(),$("#publish-story-name").val());
	});
});

/**
* Delete node providing the id of the node.
* Make a AJAX request.
*/
function deleteNode(id){
	$.ajax({
		type: 'POST'	,
		url: document.location.origin + "/api/requestDeleteNode/",
		data: {'nodeid':id,"storyid":$("#story-id").val()},
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
				if(msg.initial_node == "1") {
					$('#initial-node-section').show();
				}
				$("#node-"+id).parent().parent().empty();
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


function copyNode (id, nameNode) {
	$("#yes-copynode").unbind('click');
	$("#confirm-copynode-modal").modal("hide");
	$.ajax({
		type: 'POST'	,
		url: document.location.origin + "/api/requestCopyNode/",
		data: {'nodeid':id,"storyid":$("#story-id").val(), "namenode":nameNode},
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
				location.reload(true);
			} else {
				$("#temp-message-error").html(msg.error);
			}
		},
		error: function (thrownError) {
		    $.error(thrownError);
		}
	});

}

function publishStory(projectId,nameStory){
	$.ajax({
		type: 'POST',
		url: "../../../api/requestPublishProject/",
		data: {'projectId':projectId, "nameStory":nameStory},
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
			$("#confirm-publish-modal").modal("hide");
			if(msg.status=='ok'){
				$('#temp-message').html("<h4>The story has been published, you can find it on the publish story section.</h4>")
				$('#temp-message').fadeIn('fast');
				$('#temp-message').fadeOut(3000);
			}else{
				var msgError = msg.error;
				$('#temp-message-error').html("<h4>"+msgError+"</h4>")
				$('#temp-message-error').fadeIn('fast');
				//$('#temp-message-error').fadeOut(5000);
			}
		},
		error: function (thrownError) {
		    $.error(thrownError);
		}
	});
}