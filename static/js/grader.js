$(document).ready(function(e) {

	$('td > div > .btn').click(function() {
	    console.log("click");
      	$.ajax({
  			url: "/_assign",
  			context: document.body,
  			data: { netid: "test" }
	  	}).done(function(data) {
  			console.log(data);
	  	});
	});

});