$(document).ready(function(e) {

	console.log("bump");

	$('table tr').click(function() {
		 var href = $(this).find("a").attr("href");
		 $('#codeTitle').text(href);
		 console.log("click!");
	});
});