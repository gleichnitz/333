$(document).ready(function(e) {

	$('td > div > .btn').click(function() {
		var clickButton = $(this);
	    console.log("click");
      	$.ajax({
  			url: "/_assign",
  			context: document.body,
  			data: { netid: $('#netid').text(), id: clickButton.parent().attr('a')}
	  	}).done(function(data) {
  			clickButton.css("display", "none");
  			clickButton.parent().text(data);
	  	});
	});

});