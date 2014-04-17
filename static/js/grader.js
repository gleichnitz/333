$(document).ready(function(e) {

	$('.assignRow > td > div > .btn btn-default').click(function() {
		console.log("clicked");
      $.getJSON('/_assign_', {
        id: $(this).parent().attr('id'),
        netid: $('#netid').text()
      }, function(data) {
        console.log("success");
      });
      return false;

	});

});