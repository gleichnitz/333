$(document).ready(function() {

	$('.modal').modal({
		show: false
	});

	$('#add_buttons').click(function() {
		$('.modal').modal('toggle');
	});

	$('#manual-submit-modal').click(function() {
		var output = $(this).parent().children('input').val();
	      	$.ajax({
	  			url: "/_add_student",
	  			context: document.body,
	  			data: { netid: output }
		  	}).done(function(data) {
		  		console.log(data);
		  	});
	});

});