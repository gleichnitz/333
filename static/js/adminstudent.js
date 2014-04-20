$(document).ready(function() {

	$('.modal').modal({
		show: false
	});

	$('#add_buttons').click(function() {
		$('.modal').modal('toggle');
	});

	$('modal .btn').each(function() {
		$('.modal').modal('toggle');
	});

});