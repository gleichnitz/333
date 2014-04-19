$(document).ready(function(e) {

	$('td > div > .btn').each(function() {
		var graderType = $(this).closest('tr').children('.row_grader').text();
		$(this).closest('tr').children('.row_grader').css("color", "red");
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
		  			clickButton.closest('.grader_row').text("None");
		  		} else {
		  			clickButton.parent().parent().parent().css('display', 'none')
		  		}
		  	});			
		}

	});

});