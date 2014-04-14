$(document).ready(function(e) {

	console.log("bump");

	$('table tr #test.java').click(function() {
		 $('#codeTitle').text("test!");
		 console.log("click!");
	});
});