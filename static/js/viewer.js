$(document).ready(function(e) {

	console.log("bump");

	$('table tr #test.java').click(function() {
		 var href = $(this).find("a").attr("href");
		 $('#codeTitle').text(href);
	});
});