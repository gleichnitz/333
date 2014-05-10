$(document).ready(function() {

	$('.histo').css('display', 'none');

	$('#highChart' + $('#histoSelect').val()).css('display', 'initial');

	$('#histoSelect').change(function() {
		$('.histo').css('display', 'none');
		$('#highChart' + $(this).val()).css('display', 'initial');
	});

});