$(document).ready(function() {

	$('form').on('submit', function(event) {

		$.ajax({
			data : {
			
				email : $('#email').val(),
                recovery_ans: $('#recovery_ans').val(),
                password : $('#password').val(),
				cpassword: $('#cpassword').val(),
				
			},
			type : 'POST',
			url : '/forgetpwd'

		})
		.done(function(data) {
			
			if (!data.email_error&&!data.password_error&&!data.cpassword_error&&!data.recovery_ans_error){
				
				location.replace('http://127.0.0.1:5000/login');
				alert("Your Password has been Successfull!y Changed")
			}
			

            else if (data.email_error) {
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

			if (data.cpassword_error) {
				$('#errorAlert-cpassword').text(data.cpassword_error).show();
			}

			else{
				$('#errorAlert-cpassword').text(data.cpassword_error).hide();
			}

			if (data.recovery_ans_error) {
				$('#errorAlert-recovery_ans').text(data.recovery_ans_error).show();
			}
			else{
				$('#errorAlert-recovery_ans').text(data.recovery_ans_error).hide();
			}
			
			
			
		});

		

		event.preventDefault();

	});

});