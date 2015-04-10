/**
 * AJAX request to obtain the trends from the database
 */
var csrftoken;
$(document).ready(function(){
    csrftoken = getCookie('csrftoken');
    var options = {
		valueNames: ['node_name']
	};

    var nodeList = new List('node_content', options);
    $('#searchNode').unbind('keyup keydown');
	$('#searchNode').bind('keyup keydown',function(e) {
    	nodeList.search($(this).val());
    });

});

function sendStageData(data,projectId){
	var rootURL = window.location.origin;
	$.ajax({
		  type: 'POST'	,
		  url: rootURL+"/api/requestSaveTree/", //To reach the api url
		  data:{'json_tree':data,'project_id':projectId},
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
		  	if(msg.status== 'ok'){
			  alert("Saved");			  
			}
		  },
		  error: function (thrownError) {
		        $.error(thrownError);
		    }
		});	
}

/****************************************************************************
*
*   AJAX request the node data
*****************************************************************************/
function requestNodeData(){
    data = {"nodes":[]};
    $.each($(".element_list"),function(index,value){
        data.nodes.push($(value).val());
    });
    var rootURL = window.location.origin;
    $.ajax({
          type: 'POST'  ,
          url: rootURL+"/api/requestNodeData/", //To reach the api url
          data: data,
          async:false,
          traditional:false,
          beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                    // Send the token to same-origin, relative URLs only.
                    // Send the token only if the method warrants CSRF protection
                    // Using the CSRFToken value acquired earlier
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            },
          success: function(msg) {
            if(msg.status== 'ok'){
                initializeNode(msg);          
            }
          },
          error: function (thrownError) {
                $.error(thrownError);
            }
        }); 
}

function requestStageData(projectId,callback){

	$.ajax({
		  type: 'POST'	,
		  url: "../../../api/requestLoadTree/", //To reach the api url
		  data:{'project_id':projectId},
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
		  		
			  	if (msg.status == 'ok'){
			  		callback(msg.json);
			  	}else{
			  		callback(null);
			  	}

		  },
		  error: function (thrownError) {
		        $.error(thrownError);
		    }
		});

}