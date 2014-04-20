$(document).ready(function() {

	$('.modal').modal({
		show: false
	});

	$('#add_buttons').click(function() {
		$('.modal').modal('toggle');
	});

	$('#manual-submit-modal').click(function() {
		var output = $(this).parent().children('input').val();
		var inputfieldParent = $(this).parent().parent();
	      	$.ajax({
	  			url: "/_add_student",
	  			context: document.body,
	  			data: { netid: output }
		  	}).done(function(data) {
		  		if (data == "true") {
		  			inputfieldParent.removeClass('has-error');
		  			inputfieldParent.addClass('has-success');
		  			console.log(data);
		  		}
		  		else {
		  			inputfieldParent.addClass('has-error');
		  			inputfieldParent.removeClass('has-success');
		  			console.log(data);
		  		}
		  		console.log(data);
		  	});
	});
	$('#manual-submit-modal').click(function() {
		var output = $(this).parent().children('input').val();
		var inputfieldParent = $(this).parent().parent();
	      	$.ajax({
	  			url: "/_add_grader",
	  			context: document.body,
	  			data: { netid: output }
		  	}).done(function(data) {
		  		if (data == "true") {
		  			inputfieldParent.removeClass('has-error');
		  			inputfieldParent.addClass('has-success');
		  			console.log(data);
		  		}
		  		else {
		  			inputfieldParent.addClass('has-error');
		  			inputfieldParent.removeClass('has-success');
		  			console.log(data);
		  		}
		  	});
	});

});