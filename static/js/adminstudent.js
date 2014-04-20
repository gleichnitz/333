$(document).ready(function() {

	$('.modal').modal({
		show: false
	});

	$('#add_buttons').click(function() {
		$('.modal').modal('toggle');
	});

	$('#manual-submit-modal').click(function() {
		var output = $(this).parent().children('input').text();
		consloe.log(output);
	});

});