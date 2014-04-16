$(document).ready(function(e) {
	var firstRef = $('table tr').first().find("a").attr("href");
	$(firstRef).css("display", "initial");
	output = href.substring(1, href.length);
	$('#codeTitle').text(output);
	console.log("updated");
});