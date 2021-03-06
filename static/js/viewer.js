/*
 Project: codePost
 Template for Administrator -> Administrator -> Assignments Page
 Authors: Ayyala, Evans, Freling, Kubiak, Leichnitz
 Date: May 2014
*/

$(document).ready(function(e) {

	var firstFile = $('#codearea > div').first();
	firstFile.css("display", "initial");
	//var output = firstRef.substring(1, firstRef.length);
	$('#codeTitle').text(firstFile.attr('id'));

	$('table tr').click(function() {
		var href = $(this).attr("id");

		if (href == "" || href == "Total" || href == "total")
			return;

		var idName = href.substring(1, href.length);

		$('#codearea > div').css("display", "none");

		$('#' + idName).css("display", "initial");

		$.i18n.load(i18n_dict);
		$('#' + idName).annotator('addPlugin', 'AnnotatorViewer');
    //Annotation scroll
    $('#anotacions-uoc-panel').slimscroll({height: '100%'});

		$('#codeTitle').text(idName);
	});

	$('.given_grade').on("keyup change", function() {
   		var value = text(this.value);
   		var file = $(this).closest('tr').children('.file_name').text();
   		$.ajax({
   			url: "/_change_grade",
   			context: document.body,
   			data: {grade: value}
   		});
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
		  			clickButton.text("Unmark as Done")
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