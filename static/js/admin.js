$(document).ready(function() {

	$('#add_buttons').click(function() {
		$('#modal-add').modal('toggle');
	});

	$('.upload-button').click(function() {
		$('#modal-upload').modal('toggle');
		netid = $(this).closest('tr').children('.netid-row').children('a').children('div').text();
		$('#netid-default-field-student').attr('value', netid);
	});

	$('#.grader-close').click(function() {
		window.location.reload()
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
		var course = $('#manual-course').val()
		var inputfieldParent = $(this).parent().parent();
	      	$.ajax({
	  			url: "/_add_student",
	  			context: document.body,
	  			data: { netid: output, courseid: course }
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
		var courseName = $('#courseName').text()
		console.log(output);
	      	$.ajax({
	  			url: "/_add_grader",
	  			context: document.body,
	  			data: { netid: output, courseid: courseName }
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
		var admin = $('course-name').attr('id');
		console.log(netid);
		var thisButton = $(this);
		var toContinue = true;
		$.ajax({
  			url: "/_check_student",
  			context: document.body,
  			data: { netid: netid }
	  	}).done(function(data) {
	  		if (data == "check") {
	  			if (!confirm("You've uploaded code for this student. Are you sure you want to delete?"))
	  				toContinue = false;
	  		}

		  	if (toContinue == false)
		  		return;

      		$.ajax({
	  			url: "/_delete_student",
  				context: document.body,
  				data: { netid: netid, courseid: admin}
		  	}).done(function(data) {
		  		if (data == "true") {
	  				thisButton.closest('tr').css('display','none');
	  			} else {
	  				console.log("false");
		  		}
			});
		});
	});

	$('.delete-buttons-grader').click(function () {
		var netid = $(this).attr('id');
		console.log(netid);
		var thisButton = $(this);
		var toContinue = true;
		$.ajax({
			url: "/_check_graded_assignments",
			context:document.body,
			data: {netid: netid}
		}).done(function(data) {
			if (data == "not_empty") {
				if(!confirm("This grader has graded assignments. Are you sure you want to continue?"))
					toContinue = false;
			}

			if (toContinue == false)
				return;
			
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
	$('.grader_assignments').click(function () {
		var grader_netid = $(this).attr('id');
		var admin_netid = $(this).closest('table').parent().attr('id');
		console.log(admin_netid);
		$.ajax({
	  			url: "/admin/grader_assignments",
	  			context: document.body,
	  			data: { grader_netid: grader_netid,
	  					admin_netid: admin_netid }
		  	}).done(function(data) {
		  		if (data == "true") {
		  			console.log("true");
		  		} else {
		  			console.log("false");
		  		}
		});
	});
});