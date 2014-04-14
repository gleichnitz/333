$(document).ready(function(e) {
	var i = 0;

	console.log("bump");

	$('table tr').click(function() {
		 var href = $(this).find("a").attr("href");
		 output = href.substring(1, href.length);
		 $('#codeTitle').text(output);
		 $('#code1').css("display", "none");
		 $('#code2').css("display", "initial");
	});
});