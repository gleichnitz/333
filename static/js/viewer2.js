$(document).ready(function(e) {
	var firstRef = $('table tr').first().find("a").attr("href");
	$(firstRef).css("display", "initial");
	output = firstRef.substring(1, href.firstRef);
	$('#codeTitle').text(output);
	console.log("updated");
});