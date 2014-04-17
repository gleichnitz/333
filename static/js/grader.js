$(document).ready(function(e) {

	$('td > div > .btn').click(function() {
	   console.log("clicked");
      $.getJSON('/_assign', {
        id: "test"//$(this).parent().attr('id'),
        netid: "test" //$('#netid').text()
      }, function(data) {
        console.log(data);
      });
      return false;

	});

});