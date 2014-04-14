$(document).ready(function(e) {

	console.log("bump");

	$('table tr').click(function() {
		 var href = $(this).find("a").attr("href");
		 output = href.substring(1, href.length);
		 $('#codeTitle').text(output);
		 $('#code1').css("display", "none");
		 $('#code1').css("display", "initial");
	});
});