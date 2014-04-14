$(document).ready(function(e) {
	var i = 0;

	console.log("bump");

	$('table tr').click(function() {
		 var href = $(this).find("a").attr("href");
		 output = href.substring(1, href.length);
		 $('#codeTitle').text(output);

		 if (output == "test.java") {
		 	$('#test2.java').css("display", "none");
			$('#test.java').css("display", "initial");
		 } else {
		 	$('#test.java').css("display", "none");
			$('#test2.java').css("display", "initial");
		 }
		 
	});
});