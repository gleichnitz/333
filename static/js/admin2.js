$(document).ready(function() {

	$('#add_buttons').click(function() {
		$('#modal-add').modal('toggle');
	});

	$('.upload-button').click(function() {
		$('#modal-upload').modal('toggle');
		netid = $(this).closest('tr').children('.netid-row').children('a').children('div').text();
		console.log(netid);
		$('#netid-default-field').attr('value', netid);
	});

	$('#assignment-submit-select').change(function() {
		var assignmentSelected = $("#assignment-submit-select option:selected").text();
		var numToUpload = $("#assignment-submit-select option:selected").attr('id');
		console.log(numToUpload);

		$('#code-upload-landing').empty();

		for (var i = 0; i < numToUpload; i++) {
			var thisClone = $("#code-upload-sample").clone();
			thisClone.appendTo("#code-upload-landing");
			thisClone.css("display", "initial");
			thisClone.children('label').text("Test");
			thisClone.attr('name', assignmentSelected + i);
		}
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
		console.log("bump");
		var output = $(this).parent().children('input').val();
		var inputfieldParent = $(this).parent().parent();
		console.log(output);
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

	$('#manual-submit-modal-assignment').click(function() {
	      	$.ajax({
	  			url: "/_add_assignment",
	  			context: document.body,
	  			data: { netid: "", name: $('#assignTitle').val(), files: $('#assignFiles').val(),
	  			rubric: $('#assignPoints').val(), totalPoints: $('#totalPoints').val(), dueDate: $('#dueDate').val() }
		  	}).done(function(data) {
		  		if (data == "true") {
		  			console.log(data);
		  		}
		  		else {
		  			console.log(data);
		  		}
		  	});
	});

	$('.delete-buttons-student').click(function () {
		var netid = $(this).attr('id');
		console.log(netid);
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
		var netid = $(this).attr('id');
		console.log(netid);
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
	$('.delete-buttons-assignment').click(function () {
		var name = $(this).attr('id');
		console.log(name);
		var thisButton = $(this);
	      	$.ajax({
	  			url: "/_delete_assignment",
	  			context: document.body,
	  			data: { name: name }
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