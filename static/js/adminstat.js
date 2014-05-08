$(document).ready(function() {

	$('.histo').css('display', 'none');

	$('#histoSelect').change(function() {
		$('.histo').css('display', 'none');
		$('#highChart' + $(this).val()).css('display', 'initial');
	});

});