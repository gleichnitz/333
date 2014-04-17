$(document).ready(function(e) {

	$('.assignRow > td > div > .btn btn-default').click(function() {
      $.getJSON('/_assign_', {
        id: $(this).parent().attr('id'),
        netid: $('#netid').text()
      }, function(data) {
        console.log("success");
      });
      return false;

	});

});