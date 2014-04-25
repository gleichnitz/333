$(document).ready(function(e) {

	$('td > div > .btn').each(function() {
		var graderType = $(this).closest('tr').children().children('.row_grader').text();
		if (graderType != "None") {
			$(this).text("Release");
		}
	});

	$('td > div > .btn').click(function() {
		var clickButton = $(this);
		var buttonType = clickButton.text()

		if (buttonType == "Claim") {
	      	$.ajax({
	  			url: "/_assign",
	  			context: document.body,
	  			data: { netid: $('#netid').text(), id: clickButton.parent().attr('id')}
		  	}).done(function(data) {
		  		if (data == "success") {
		  			clickButton.text("Release");
		  			clickButton.closest('tr').children().children('.row_grader').text($('#netid').text());
		  			clickButton.closest('tr').children().children('.graded_status').text('In Progress');
		  			// Update grader field
		  		} else {
		  			clickButton.parent().parent().parent().css('display', 'none')
		  		}
		  	});
		} else {
	      	$.ajax({
	  			url: "/_release",
	  			context: document.body,
	  			data: { netid: $('#netid').text(), id: clickButton.parent().attr('id')}
		  	}).done(function(data) {
		  		if (data == "success") {
		  			clickButton.text("Claim");
		  			clickButton.closest('tr').children().children('.row_grader').text("None");
		  			clickButton.closest('tr').children().children('.graded_status').text('--------');
		  		} else {
		  			clickButton.parent().parent().parent().css('display', 'none');
		  		}
		  	});			
		}
	});

});