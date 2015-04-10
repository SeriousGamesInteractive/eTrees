
var csrftoken;
$(document).ready(function(){
	csrftoken= getCookie('csrftoken');

	$(".messages").fadeOut(6000);
	$('.delete-button').click(function(){
		var asset = $(this).attr('id');
		asset = asset.split('-');
		requestDeleteAsset(asset[1],asset[0]);
	})
	
	$('#libraryTab a:first').tab('show');

	if($('#saved-asset').val()){
		$('#'+$('#saved-asset').val()+'-tab').tab('show');
	}

	//Control the asset
	$(".asset-content").click(function(){
		var id = $(this).parent().attr("id").split("_");
		requestContentAsset(id[2],id[1]);//parameter: assetid, assettype
		
	});
});

/**
 * AJAX request to delete asset
 */
function requestDeleteAsset(assetId,assetType){
	var libraryId = $('#library-id').val();
	$.ajax({
		  	type: 'POST'	,
		  	url: "../../../api/requestDeleteAsset/",//To reach the api url
		  	data:{'asset_id':assetId,'asset_type':assetType,'lib_id':libraryId},
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
			  $('#row_'+assetType+'_'+assetId).empty();			  
		  	},
		  	error: function (thrownError) {
		        $.error(thrownError);
		    }
	});
	
}


/**
 * AJAX request to obtain the content of the asset
 */
function requestContentAsset(assetId,assetType){
	var libraryId = $('#library-id').val();
	$.ajax({
		  type: 'POST'	,
		  url: "../../../api/requestContentAsset/",//To reach the api url
		  data:{'asset_id':assetId,'asset_type':assetType
		},
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
		  	//Get the path of the asset
		  	var date = new Date();
		  	switch(assetType){
		  		case 'audio':
		  			$("#asset-content-body").html('<audio controls><source src="'+msg.path+'?'+date.getDate()+'" type="audio/mpeg">'+
		  				'Your browser does not support the audio element.</audio>');
		  			break;
		  		case 'background':
		  			$("#asset-content-body").html('<img src="'+msg.path+'?'+date.getDate()+'" height="300">');
		  			break;
		  		case 'graphic':
		  			$("#asset-content-body").html('<img src="'+msg.path+'?'+date.getDate()+'" height="300">'
		  			);
		  			break;
		  		case 'animation':
		  			var flashvars = {};
					var params = {
						   	path: "false",
						   	scale: "noScale",
						   	quality : "high",
						   	allowFullscreen: "true",
							allowScriptAccess: "always",
							bgcolor: "",
							wmode: "direct" // can cause issues with FP settings & webcam
					};
					var attributes = {
							id:"asset-animation-content",
							name:"asset-animation-content"
					};					
		  			$("#asset-content-body").html(
		  				'<div id="asset-animation-content"></div>'
		  			);
		  			swfobject.embedSWF(msg.path, "asset-animation-content",  "100%", "80%", "10.0.0", false, flashvars, params, attributes);
		  			break;	
		  		default:
		  			return;	
		  	}
		  	$("#asset-content-title").html('<p>'+msg.name+'</p>');
			$("#content-assets-modal").modal('show');
		  },
		  error: function (thrownError) {
		        $.error(thrownError);
		    }
		});
	
}

