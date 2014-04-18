$(document).ready(function() {

	$('.modal').modal({
		show: false
	});

	$('#modalButton').click(function() {
		$('.modal').modal('toggle');
	});
    
    $('#add_mult_students').hover(function() {
      $(this).tooltip();
    });



});