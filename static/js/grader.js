$(document).ready(function(e) {

<<<<<<< HEAD
	$('.assignRow > td > div > .btn btn-default').click(function() {
      $.getJSON('/_assign_', {
        id: $(this).parent().attr('id'),
        netid: $('#netid').text()
      }, function(data) {
        console.log("success");
      });
      return false;

=======
	$('td > div > .btn').click(function() {
		var clickButton = $(this);
	    console.log("click");
      	$.ajax({
  			url: "/_assign",
  			context: document.body,
  			data: { netid: "jaevans" }
	  	}).done(function(data) {
  			clickButton.css("display", "none");
  			clickButton.parent().text(data);
	  	});
>>>>>>> c9b19238236162079e87a867f921a25137c6bc93
	});

});