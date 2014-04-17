$(document).ready(function(e) {

	$('td > div > .btn').click(function() {
	   console.log("click");
      $.ajax({
  		url: "/_assign",
  		context: document.body
	  }).done(function() {
  		console.log("success");
	  });
});