$(document).ready(function(e) {

    $SCRIPT_ROOT = {{ request.script_root|tojson|safe }};

	$('td > div > .btn').click(function() {
	   console.log("click");
      $.ajax({
  		url: "/_assign",
  		context: document.body
	  }).done(function() {
  		console.log("success");
	  });
});