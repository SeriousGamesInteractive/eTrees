$(document).ready(function(){


	var isTrainer = $("#is-trainer").val();
	if (isTrainer =="True") {
		$("#button-admin-user").hide();
		$("#show-trainer-content").hide();
	}
	$('#box-newuser').click(function(){
		showFormulary('create-user',['change-settings','create-trainer']);
	});
	$('#box-trainer-newuser').click(function(){
		showFormulary('create-trainer',['change-settings','create-user']);
	});
	$('#box-settings-account').click(function(){
		showFormulary('change-settings',['create-user','create-trainer']);
	});

	$('.login-password').unbind("keydown keyup");
	$('.login-password').bind("keydown keyup",function(){
		if ($('#inputLoginPassword').val() == $('#inputLoginPasswordConfirm').val() && $('#inputLoginPassword').val()!= "") {
			$('#loginSave').prop('disabled',false);
			$('#inputLoginPassword').parent().children('.warning-message').text('');
		}else{
			$('#loginSave').prop('disabled',true);
			$('#inputLoginPassword').parent().children('.warning-message').text("The passwords must be the same.");
		}
	});
	$('.password').unbind("keydown keyup");
	$('.password').bind("keydown keyup",function(){
		if ($('#inputPassword').val() == $('#inputPasswordConfirm').val() && $('#inputPassword').val() != "") {
			$('#save').prop('disabled',false);
			$('#inputPassword').parent().children('.warning-password-message').text('');
		}else{
			$('#save').prop('disabled',true);
			$('#inputPassword').parent().children('.warning-password-message').text("The passwords must be the same.")
		}
	});
	$('.trainer-password').unbind("keydown keyup");
	$('.trainer-password').bind("keydown keyup",function(){
		if ($('#inputTrainerPassword').val() == $('#inputTrainerPasswordConfirm').val() && $('#inputTrainerPassword').val() != "") {
			$('#trainer-save').prop('disabled',false);
			$('#inputTrainerPassword').parent().children('.warning-password-message').text('');
		}else{
			$('#trainer-save').prop('disabled',true);
			$('#inputTrainerPassword').parent().children('.warning-password-message').text("The passwords must be the same.")
		}
	});
	var type= $('#saved-type').val();
	if (type=="loginuser"){
		showFormulary('change-settings',['create-user','create-trainer']);
	}else if (type=="createuser"){
		showFormulary('create-user',['change-settings','create-trainer']);
	} else if (type=="createtrainer") {
		showFormulary('create-trainer',['change-settings','create-user']);
	}
	
	$(".message").fadeOut(3000);
});

function showFormulary(formshow, formhide){
	$('.box-option').animate({
			height: "100px"
		},2000,function(){});
		$('#'+formshow).show();
		$.each(formhide,function( index,value){
			$('#'+value).hide();
		});
		
}