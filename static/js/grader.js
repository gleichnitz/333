$(document).ready(function(e) {

    $SCRIPT_ROOT = {{ request.script_root|tojson|safe }};

	$('td > div > .btn').click(function() {
	   console.log("clicked");
      $.ajax($SCRIPT_ROOT + '/_assign', {
        id: "test", //$(this).parent().attr('id'),
        netid: "test" //$('#netid').text()
      }, function(data) {
        console.log(data);
      });
      return false;

	});

});