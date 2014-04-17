$(document).ready(function(e) {

	$('.assignRow > td > div > .btn btn-default').click(function() {
      $.getJSON('/_assign_', {
        id: $(this).parent().attr('id'),
        netid: $('#netid').text()
      }, function(data) {
        $(this).parent().text(data.result);
      });
      return false;

	});

});