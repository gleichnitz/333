$(document).ready(function() {

	$('.modal').modal({
		show: false
	});

	$('#add_buttons').click(function() {
		$('.modal').modal('toggle');
	});

});