$(document).ready(function(e) {
	var firstRef = $('table tr').first().find("a"); //.find("a").attr("href");
	console.log(firstRef.attr("href"));
	//$(firstRef).css("display", "initial");
	var output = firstRef.substring(1, firstRef.length);
	$('#codeTitle').text(output);
	console.log("updated");
});