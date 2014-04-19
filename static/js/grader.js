$(document).ready(function(e) {

	$('td > div > .btn').click(function() {
		var clickButton = $(this);
		var buttonType = clickButton.text()

      	$.ajax({
  			url: "/_assign",
  			context: document.body,
  			data: { netid: $('#netid').text(), id: clickButton.parent().attr('id')}
	  	}).done(function(data) {
	  		if (data == "success") {
	  			clickButton.text("Release");
	  			// Update grader field
	  		} else {
	  			clickButton.parent().parent().css('display', 'none')
	  		}
	  	});
	});

});