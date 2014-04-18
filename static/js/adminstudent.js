$(document).ready(function() {

	$('.modal').modal({
		show: false
	});

	$('#add_buttons').click(function() {
		$('.modal').modal('toggle');
	});
    
    $('#add_mult_students').hover(function() {
      $(this).tooltip();
    });



});