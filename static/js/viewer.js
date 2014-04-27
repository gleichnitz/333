$(document).ready(function(e) {

	var firstFile = $('#codearea > div').first();
	firstFile.css("display", "initial");
	//var output = firstRef.substring(1, firstRef.length);
	$('#codeTitle').text(firstFile.attr('id'));

	$('table tr').click(function() {
		var href = $(this).attr("id");
		var idName = href.substring(1, href.length);

		$('#codearea > div').css("display", "none");

		$('#' + idName).css("display", "initial");
		$('#codeTitle').text(idName);
	});

	$('.given_grade').on("keyup change", function() {
   		var value = text(this.value);
   		var file = $(this).closest('tr').children('.file_name').text()
   		$.ajax({
   			url: "/_change_grade",
   			context: document.body,
   			data: {grade = value, file=file}
   		)};
  //  		}).done(function(data) {
	 // 		if (data == "success") {
	 			
		//   	} else {

	 //  		}
		// });
	});

	$('#mark_as_done').click(function() {
		var assignmentid = $(this).closest(".table").attr('id')
		var clickButton = $(this)
		var state = clickButton.text()
		if (state == "Mark Grading as Done") {
			$.ajax({
				url: "/_done",
	  			context: document.body,
	  			data: { id: assignmentid}
			}).done(function(data) {
		 		if (data == "success") {
		  			clickButton.text("Edit Again")
		  		} else {

		  		}
			});
		}
		else {
			$.ajax({
				url: "/_undone",
	  				context: document.body,
	  				data: { id: assignmentid}
			  	}).done(function(data) {
			  		if (data == "success") {
			  			clickButton.text("Mark Grading as Done")
			  			// Update grader field
		  			} else {

			  		}
			});
		}
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