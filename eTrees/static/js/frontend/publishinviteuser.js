var csrftoken;
var storiesObj = [];

/**********************
* storyObj javascript object 
* to save the content for each story 
* locally in the client
***********************/
function StoryObj (id) {
	this.id = id;
	this.namestory = "";
	this.users =[];

	this.addUsers = function(user) {
		this.users.push({"name":user.name,"surname":user.surname,"username":user.username,"id":user.id});
		this.updateParticipants();
	};

	this.removeUsersById = function(userIDs) {
		for (var i = 0; i < userIDs.length; i++) {
			this.removeUserById(userIDs[i]);
		}
	}
	
	this.removeUserById = function(userID) {
		var newUsers = [];
		for (var i = 0; i < this.users.length; i++) {
			if (this.users[i].id != userID) {
				newUsers.push(this.users[i]);
			}
		}
		
		this.users = newUsers;
		
		this.updateParticipants();
		
		$("#user_story-"+this.id).html(' '+this.users.length +" participants ");
	};
	
	this.updateParticipants = function() {
		$("#user_story-"+this.id).html(' '+this.users.length +" participants ");
	};
}
//Function to obtain the story from the array of stories
function getStoryObj(id) {
	for (var i = 0; i < storiesObj.length; i++) {
		var storyTemp = storiesObj[i];
		if ( storyTemp.id == id) {
			return storyTemp;
		}
	}
	return null;
}

$(document).ready(function(){
    csrftoken = getCookie('csrftoken');

    //Obtain the participants for each story
    getParticipantsStories();
    
	$(".btn-user-not-add").bind("click",function(){
		selectUser(this);
	});
	$(".box-story").click(function(){
		var storyId = $(this).attr("id").split("-")[1];
		var leftPos =$(this).offset().left - 75;
		var topPos =$(this).offset().top + 50; 
		//Check if there is at least one user is selected
		if($(".btn-user-add").length != 0){
			inviteUserToStory(storyId,leftPos,topPos);
		}
	});
	$('#import-user').hide();
	$('#import-more').click(function(){
		$('#import-user').fadeIn(2000);
		$(this).fadeOut("fast");
	});

	//Controll request users invite 
	$('.icon-num-users').mouseover(function(){
		$(this).parent().bind('click',false);
	});
	$('.icon-num-users').mouseout(function(){
		$(this).parent().unbind('click',false);
	});
	$('.icon-num-users').bind('click',function(){
		var leftPos =$(this).offset().left - 75;
		var topPos =$(this).offset().top + 50;
		var storyId = $(this).children().attr("id").split("-")[1];
		requestUserInvitedStory(storyId,leftPos,topPos);		
	});

	$("#select-aĺl").bind('click',function() {
		$(".invite-button button").each(function() {
			selectUser(this);
		});
	});

	//Search user implementation
	var options = {
		valueNames: ['user-name','user-surname','user-username']
	};
	//List control the search functionlity on the list
	var userList = new List('usergame-container', options);
	$("#inputSearchUser").unbind('keyup keydown');
	$("#inputSearchUser").bind('keyup keydown',function(e) {
		
		userList.search($(this).val());
	});
 });


/***
 Select user
***/

function selectUser(userObj) {
	$(userObj).toggleClass("btn-user-not-add");
	$(userObj).toggleClass("btn-user-add");
	if($(userObj).html() == ""){
		$(userObj).html("Add");
	}else{
		$(userObj).html("");
	}
	$(userObj).toggleClass("btn-primary");
	$(userObj).toggleClass("btn-default");
}
/************************************
*	AJAX request 
*	Request the participants for each story
*	instanciate the storyObj for each of the stories, including each participant
*************************************/
function getParticipantsStories() {
	var data ={"stories":[]};
    $.each($(".publish-stories"),function(index,value){
    	data.stories.push($(value).attr("id").split("-")[1]);
    });
    //There is no projects
    if (data.stories.length==0) {
    	return;
    }
    var rootURL = window.location.origin;    
    $.ajax ({
   		type: 'POST',
	  	url: rootURL+"/api/requestUsersOnStories/",//To reach the api url
	  	data:data,
	  	async:false,
	  	traditional:true,
	  	beforeSend: function(xhr, settings) {
	        if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
	            // Send the token to same-origin, relative URLs only.
	            // Send the token only if the method warrants CSRF protection
	            // Using the CSRFToken value acquired earlier
	            xhr.setRequestHeader("X-CSRFToken", csrftoken);
	        }
	    },
		success: function(msg) {
			//Create the storyObj to add the information of the users and the stories
			for (var i = 0; i < msg.stories.length; i++) {
				var storyObjTemp = new StoryObj(msg.stories[i].storyid);
				storyObjTemp.storyname = msg.stories[i].storyname;
				for (var j = 0; j < msg.stories[i].users.length;j++) {
					storyObjTemp.addUsers(msg.stories[i].users[j]);
				}
				storiesObj.push(storyObjTemp);
			}
		},
		error: function (thrownError) {
		    $.error(thrownError);
		}
	});
}

function inviteUserToStory(storyId,leftPos,topPos) {
	//Get id of the users
	var usersId = [];
	$.each($(".btn-user-add"),function(index,value) {
		usersId.push(parseInt($(value).attr("id").split("-")[1]));
	});
	//Get the story
	var storyObjTemp = getStoryObj(storyId);
	if(storyObjTemp != null) {
		for(var i=0;i < storyObjTemp.users.length; i++) {
			var userId = storyObjTemp.users[i].id;
			var index = usersId.indexOf(userId);
			if(index != -1) {
				//Remove element from the list
				usersId.splice(index,1);	
			}
		}
	}

	//Show modal window to confirm that you want to add those user to the story
	contentFooterHtml = '<button type="button" id="accept-invitation" class="btn btn-success" >Invite</button>';
	contentFooterHtml += '<button type="button" class="btn btn-default" data-dismiss="modal">Close</button>';
	var contentHtml = "";
	contentHtml += '<h5>Do you want to invite:</h5>';
	contentHtml += '<div class="user-list-invited">'
	contentHtml  += "<ul>";
	for (var i =0; i < usersId.length;i++){
		//The name and surname are saved as input type hidden, the first next refers 
		contentHtml +="<li> "+$("#nameuser-"+usersId[i]).val() + " " + $("#surnameuser-"+usersId[i]).val() +" </li>";
	}
	if(usersId.length == 0) {
		contentHtml +="<li> User/s selected are already in this story </li>";
		contentFooterHtml = '<button type="button" class="btn btn-default" data-dismiss="modal">Close</button>';
	}
	contentHtml +="</ul></div>";
	contentHtml += '<h5>to the story "' +storyObjTemp.storyname+ '"</h5>';
	contentHtml += '<label for="extraMessage">Custom text </label>';
	contentHtml += '<textarea class="form-control" name="extra-message" id="extraMessage" placeholder="Add extra content to the email"></textarea>';
	contentHtml +="</div>";

	
	showModalInviteUsers(leftPos,topPos,contentHtml,contentFooterHtml);
	$("#accept-invitation").click(function(){
		var extraMessage = $("#extraMessage").val();
		addUserStory(storyId,usersId,leftPos,topPos, extraMessage);
	});
	
}

/*********************************************
AJAX request addUserStory
	paremeters:
		storyId: id of the story 
		leftPos: left pixels of the element clicked
		topPos: top pixels of the element clicked
**********************************************/
function addUserStory(storyId,usersId,leftPos,topPos, extraMessage) {
	var data = {"idstory":storyId,"users":usersId, "extraMessage": extraMessage};
	var rootURL = window.location.origin; 
	$.ajax({
	  	type: 'POST'	,
	  	url: rootURL+"/api/requestAddUserStory/",//To reach the api url
	  	data:data,
	  	async:false,
	  	traditional:true,
	  	beforeSend: function(xhr, settings) {
	        if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
	            // Send the token to same-origin, relative URLs only.
	            // Send the token only if the method warrants CSRF protection
	            // Using the CSRFToken value acquired earlier
	            xhr.setRequestHeader("X-CSRFToken", csrftoken);
	        }
	    },
		success: function(msg) {
			if(msg.status == "ok") {
				var storyObjTemp = getStoryObj(storyId);
				for(var i = 0; i < msg.users_added.length; i++){
					storyObjTemp.addUsers(msg.users_added[i]);
				}

				contentFooterHtml = "Invitation sent!  ";
				contentFooterHtml +='<button type="button" class="btn btn-default" data-dismiss="modal">Close</button>';
				showModalInviteUsers(leftPos,topPos,null,contentFooterHtml);
			} else {
				contentFooterHtml = "Error: "+msg.error;
				contentFooterHtml +='<button type="button" class="btn btn-default" data-dismiss="modal">Close</button>';
				showModalInviteUsers(leftPos,topPos,null,contentFooterHtml);
			}
		},
		error: function (thrownError) {
		    $.error(thrownError);
		}
	});
}

function requestUserInvitedStory(storyId,leftPos,topPos) {

	var storyObjTemp=getStoryObj(storyId);
	if (storyObjTemp != null) {
		contentHtml = "";
		contentHtml += '<div class="title-modal"> "'+storyObjTemp.storyname +'"</div>';
		contentHtml += '<h5>These users are invited:</h5>';
		contentHtml += '<div class="user-list-invited" style="overflow: hidden;">';
		contentHtml  += "<select multiple style=\"width: 100%; height: 100%;\" id=\"user-list\">";
		for (var i =0; i < storyObjTemp.users.length;i++){
			var user = storyObjTemp.users[i];
			contentHtml +="<option selected=\"selected\" value=\"" + user.id + "\"> "+user.name + " " + user.surname +" </option>";
		}
		contentHtml +="</select>";
		contentHtml +="</div>";
		contentFooterHtml= '<button type="button" class="btn btn-success" data-dismiss="modal" id="save-users">Save</button> <button type="button" class="btn btn-default" data-dismiss="modal">Close</button>';
		showModalInviteUsers(leftPos,topPos,contentHtml,contentFooterHtml);
		
		$('#save-users').click(function(e) {
			e.stopPropagation();
			e.preventDefault();
			
			var btn = $(this);
			
			if (btn.hasClass('disabled')) {
				return;
			}
			
			btn.addClass('disabled');
			
			var removedUsers = $('select#user-list option:not(:selected)');
			
			if (removedUsers.length) {
				var removedUserIDs = [];
				
				for (var i = 0; i < removedUsers.length; i++) {
					removedUserIDs.push(parseInt(removedUsers.eq(i).val(), 10));
				}
				
				var rootURL = window.location.origin; 
				$.ajax({
					type: 'POST'	,
					url: rootURL+"/api/requestRemoveUserStory/",//To reach the api url
					data:{
						userIDs: removedUserIDs,
						idstory:storyId
					},
					async:false,
					traditional:true,
					beforeSend: function(xhr, settings) {
						if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
							// Send the token to same-origin, relative URLs only.
							// Send the token only if the method warrants CSRF protection
							// Using the CSRFToken value acquired earlier
							xhr.setRequestHeader("X-CSRFToken", csrftoken);
						}
					},
					success: function(msg) {
						if(msg.status == "ok") {
							$("#modal-invite-users").modal('hide');
							
							for (var i = 0; i < storiesObj.length; i++) {
								if (storiesObj[i].id == storyId) {
									storiesObj[i].removeUsersById(removedUserIDs);
									
									break;
								}
							}
						} else {
							alert(msg.error);
						}
						btn.removeClass('disabled');
					},
					error: function (thrownError) {
						btn.removeClass('disabled');
						
						$.error(thrownError);
					}
				});
			} else {
				alert('Nothing to save!');
				btn.removeClass('disabled');
			}
		});
	}
}

/**
*	Show the modal window with the format established for the invite user.
*/
function showModalInviteUsers(leftPos,topPos,content,contentFooter) {
	var leftWindow =$(window).width();
	var topWindow = $(window).height();		
	var modalDiv =$("#modal-invite-users");
	topPos = topPos - parseInt(modalDiv.css("width"));
	leftPos= (leftPos * 100) / leftWindow;
	topPos = (topPos * 100) / topWindow;
	modalDiv.css("left",""+leftPos+"%");
	modalDiv.css("top",""+topPos+"%");
	if(content){
		$(modalDiv.children().children().children()[0]).html(content);
	};
	if(contentFooter) {
		$(".modal-footer").html(contentFooter);

	}
	modalDiv.modal("show");
}