$(document).ready(function(e) {
	var i = 0;

	console.log("bump");

	$('table tr').click(function() {
		 var href = $(this).find("a").attr("href");
		 output = href.substring(1, href.length);
		 $('#codeTitle').text(output);

		 if (output == "test") {
		 	$('#test2').css("display", "none");
			$('#test').css("display", "initial");
		 } else {
		 	$('#test').css("display", "none");
			$('#test2').css("display", "initial");
		 }
		 
	});
});