
$(document).ready(function(){
	$('#import-user').hide();
	$('#import-more').click(function(){
		$('#import-user').fadeIn(2000);
		$(this).fadeOut("fast");
	});

});