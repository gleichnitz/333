$(document).ready(function() {

	$('#histoSelect').change(function() {
		$('.histo').css('display', 'none');
		$('#highChart' + $(this).val()).css('display', 'initial');
	});

});