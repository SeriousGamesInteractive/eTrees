$(document).ready(function(){
	"use strict";
  var csrftoken= getCookie('csrftoken');


  var templateCategory ='<div class="form-group category-div group-category" id="{{group-id}}" >\
                    <div class="col-lg-4 col-md-4" >\
                      <label for="{{name-id}}">{{label-name}}</label>\
                      <input type="text" class="form-control name-category" name="{{name-id}}" maxlength="100" id="{{name-id}}" placeholder="Name category">\
                    </div>\
                    <br>\
                    <div class="col-lg-3 col-md-3 select-category">\
                      <label for="{{maxvalue-id}}">Max value</label>\
                      <select name="{{maxvalue-id}}" id="{{maxvalue-id}}">\
                        <option value="0">0</option>\
                        <option value="1">1</option>\
                        <option value="2">2</option>\
                        <option value="3">3</option>\
                        <option value="4">4</option>\
                        <option value="5">5</option>\
                      </select>\
                    </div>\
                    <div class="col-lg-3 col-md-3 select-category"> \
                    <label for="{{minvalue-id}}">Min value</label>\
                      <select name="{{minvalue-id}}" id="{{minvalue-id}}">\
                        <option value="0">0</option>\
                        <option value="-1">-1</option>\
                        <option value="-2">-2</option>\
                        <option value="-3">-3</option>\
                        <option value="-4">-4</option>\
                        <option value="-5">-5</option>\
                      </select>\
                    </div>\
                    <div class="col-lg-1 col-md-1 button-del-category">\
                      <button class="btn btn-danger button-category" value="{{group-id}}">Del</button>\
                    </div>\
                    <div class="col-lg-12 col-md-12">\
                      <textarea style="resize:vertical;" class="form-control" name="{{description-id}}" id="inputDescription"\
                      placeholder="Add a description of the category"></textarea>\
                    </div>\
                  </div>';
	//CHeck if the library dropdown menu has options or not
	if($('#select-library').has('option').length < 1){
		$('.warning-message').text("You need to create a library before creating a story");
		$('.warning-message').css('display','block');
	}
    //Check the Submit

    $("#form-editstory").submit(function(event) {
        var messageWarning = $(".warning-message");
        var dictNames = {};
        $.each($(".name-category"), function(index, element) {
            if(dictNames[element.value] !== undefined) {
                event.preventDefault();
                messageWarning.html("Story cannot be saved, two or more categories have the same name.");                
                return false;
            }
            dictNames[element.value]= true;
        });
    });

    $("#form-createstory").submit(checkForm);

	//Create new attributes
	var categoryCounter = parseInt($("#numberCategories").val()) | 0;
	var compiledTemplate = Handlebars.compile(templateCategory);
	$("#addCategory").bind('click',function() {		
		if(categoryCounter <= 10) { 
			var html = compiledTemplate({"group-id": 'category'+categoryCounter,"label-name": 'Name category '+ (categoryCounter+1),
       "name-id":'nameCategory'+categoryCounter, "maxvalue-id":'maxvalue'+categoryCounter,"minvalue-id":'minvalue'+categoryCounter,
       "description-id":'descriptionCategory'+categoryCounter});
			$("#category-add").append(html);
      categoryCounter++;
      $("#numberCategories").val(categoryCounter);
      $(".button-category").unbind('click');
      $(".button-category").bind('click',function(evt) {
        //Delete category and reset the number of "numberCategories" variable and the counter.
        evt.preventDefault();
        categoryCounter--;
        $("#numberCategories").val(categoryCounter);
        $(this).parent().parent().remove();
      });
		}
  });

  //Include the control of the delete when the story has to be copied by deleting the elements in the DOM, not in the database
  $(".button-category").unbind('click');
  $(".button-category").bind('click',function(evt) {
    //Delete category and reset the number of "numberCategories" variable and the counter.
    evt.preventDefault();
    categoryCounter--;
    $("#numberCategories").val(categoryCounter);
    $(this).parent().parent().remove();
  });
  //In the case it is a edit story page or copy story, it has to be handle the deletion of categories
    $(".category-button-delete").unbind('click');
    $(".category-button-delete").bind('click',function(evt) {
      //Delete category and reset the number of "numberCategories" variable and the counter.
      evt.preventDefault();
      var respond = confirm("Do you want to delete this category? (This is a permanent change)");
      if (respond === true) {
        var value = $(this).val(); //The value contains the id of the project and the id of the category
        var scope = $(this);
        $.ajax({
          type: 'POST'  ,
          url: "/api/requestDeleteCategory/",
          data:{'projectid':value.split("-")[0],'categoryid':value.split("-")[1]},
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
            //Remove the element from the page
            categoryCounter--;
            $("#numberCategories").val(categoryCounter);
            scope.parent().parent().remove();
            
          },
          error: function (thrownError) {
                $.error(thrownError);
            }
        });
      }
    });

    //  
    $("#save-button").unbind('click');
    $("#save-button").bind('click', function(evt) {
        evt.preventDefault();
        if(categoryCounter === 0) {
            var respond = confirm("There is not categories assigned to the story, do you want to continue?");
            if (respond === true) {
                $("#form-createstory").trigger("submit");
            } else {
                return;
            }
        }else{
          $("#form-createstory").trigger("submit");
        }
    });

    $("#delete-story").unbind('click');
    $("#delete-story").bind('click', function(evt) {
        evt.preventDefault();
      
        var respond = confirm("Are you sure you want to delete the story?");
        if (respond === true) {
            $("#delete-story").unbind('click');
            $("#delete-story").trigger("click");
        } else {
            return;
        }

        
    });

	
});



/**
* Check the story form:
*   - InputName
*   - InputTopic
*   - Libraries selected
*   - Categories added
*   
**/

function checkForm(event) {
    var messageWarning = $(".warning-message");
    var dictNames = {};
    $.each($(".name-category"), function(index, element) {
        if(dictNames[element.value] !== undefined) {
            event.preventDefault();
            messageWarning.html("Story cannot be saved, two or more categories have the same name.");                
            return false;
        }
        dictNames[element.value]= true;
    });

    //Check the name input
    if($("#inputName").val() == "") {
        event.preventDefault();
        messageWarning.html("Enter a name for the story");                
        return false;
    }
    //Check the topic input
    if($("#inputTopic").val() == "") {
        event.preventDefault();
        messageWarning.html("Enter a topic for the story");                
        return false;
    }

    //Check the topic input
    var multipleLibraries = $("#select-library").val() || [];
    if(multipleLibraries.length == 0) {
        event.preventDefault();
        messageWarning.html("You have to select a library for the story");                
        return false;
    }
    
}