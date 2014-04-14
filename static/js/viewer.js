$(document).ready(function(e) {

	console.log("bump");

	$('table tr').click(function() {
		 var href = $(this).find("a").attr("href");
		 output = href.substring(1, href.length);
		 $('#codeTitle').text(output);
		 $('#codeLocus').ajax({
            url : "test2.java",
            dataType: "java",
         });
	});
});