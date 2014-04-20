$(document).ready(function() {

	$('.modal').modal({
		show: false
	});

	$('#add_buttons').click(function() {
		$('.modal').modal('toggle');
	});

	$('#manual-submit-modal-student').click(function() {
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
		  	});
	});

	$('#manual-submit-modal-grader').click(function() {
		var output = $(this).parent().children('input').val();
		var inputfieldParent = $(this).parent().parent();
	      	$.ajax({
	  			url: "/_add_grader",
	  			context: document.body,
	  			data: { name: output }
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

	$('#manual-submit-modal-assignment').click(function() {
		var output = $(this).parent().children('input').val();
		var inputfieldParent = $(this).parent().parent();
	      	$.ajax({
	  			url: "/_add_assignment",
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

	$('.delete-buttons-student').click(function () {
		var netid = $(this).closest('tr').children('.netid-row').text();
		var thisButton = $(this);
	      	$.ajax({
	  			url: "/_delete_student",
	  			context: document.body,
	  			data: { netid: netid }
		  	}).done(function(data) {
		  		if (data == "true") {
		  			thisButton.closest('tr').css('display','none');
		  		} else {
		  			console.log("false");
		  		}
		});
	});

	$('.delete-buttons-grader').click(function () {
		var netid = $(this).closest('tr').children('.netid-row').text();
		var thisButton = $(this);
	      	$.ajax({
	  			url: "/_delete_grader",
	  			context: document.body,
	  			data: { netid: netid }
		  	}).done(function(data) {
		  		if (data == "true") {
		  			thisButton.closest('tr').css('display','none');
		  			console.log("true");
		  		} else {
		  			console.log("false");
		  		}
		});
	});

});