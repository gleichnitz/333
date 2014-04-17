$(document).ready(function(e) {

	$('.assignRow > td > div > .btn btn-default').click(function() {
      $.getJSON('/_add_numbers', {
        id: $(this).parent().attr('id'),
        netid: $('#netid').text()
      }, function(data) {
        $(this).parent().text(data.result);
      });
      return false;

	});

});