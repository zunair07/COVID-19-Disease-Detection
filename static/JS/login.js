$(document).ready(function() {

	$('form').on('submit', function(event) {

		$.ajax({
			data : {
				email : $('#email').val(),
                password : $('#password').val()
			},
			type : 'POST',
			url : '/login'

		})
		.done(function(data) {
			
			if (!data.email_error&&!data.password_error){
				location.replace('http://127.0.0.1:5000');
			}
			

            if (data.email_error) {
				$('#errorAlert-email').text(data.email_error).show();
			}
			else{
				$('#errorAlert-email').text(data.email_error).hide();
			}

            if (data.password_error) {
				$('#errorAlert-password').text(data.password_error).show();
			}

			else{
				$('#errorAlert-password').text(data.password_error).hide();
			}

			
			
			
			
		});

		

		event.preventDefault();

	});

});