$(document).ready(function(e) {

	var firstFile = $('#codearea > div').first();
	firstFile.css("display", "initial");
	//var output = firstRef.substring(1, firstRef.length);
	$('#codeTitle').text(firstFile.attr('id'));

	$('table tr').click(function() {
		var href = $(this).attr("id");
		var idName = href.substring(1, href.length);
		$('codearea > div').css("display", "none");
		$('#' + idName).css("display", "initial");
	});

	/* $('table tr').click(function() {
		 var href = $(this).find("a").attr("href");
		 output = href.substring(1, href.length);
		 $('#codeTitle').text(output);

		 if (output == "test") {
		 	$('#test2').css("display", "none");
		 	$('#test3').css("display", "none");
			$('#test').css("display", "initial");
		 } else if (output == "test2") {
		 	$('#test').css("display", "none");
		 	$('#test3').css("display", "none");
			$('#test2').css("display", "initial");
		 } else {
		 	$('#test').css("display", "none");
		 	$('#test2').css("display", "none");
			$('#test3').css("display", "initial");
		 }
		 
	}); */
});