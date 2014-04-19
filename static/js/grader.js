$(document).ready(function(e) {

	$('td > div > .btn').click(function() {
		var clickButton = $(this);

      	$.ajax({
  			url: "/_assign",
  			context: document.body,
  			data: { netid: $('#netid').text(), id: clickButton.parent().attr('id')}
	  	}).done(function(data) {
  			clickButton.css("display", "none");
  			clickButton.parent().text(data);
	  	});
	});

});