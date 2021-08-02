$(document).ready(function() {

	$('form').on('submit', function(event) {

		$.ajax({
			data : {
                cnic:$('#cnic').val(),
				name : $('#patientname').val(),
                age : $('#age').val(),
                contactnum: $('#contactnum').val(),
				gender : $('#gender').val(),
			},
			type : 'POST',
			url : '/patientdetails'

		})
		.done(function(data) {
			
			if (!data.cnic_error&&!data.name_error&&!data.gen_error && !data.age_error){
				location.replace('http://127.0.0.1:5000/file_upload');
			}
			

            if (data.cnic_error) {
				$('#errorAlert-pcnic').text(data.cnic_error).show();
			}
			else{
				$('#errorAlert-pcnic').text(data.cnic_error).hide();
			}

            if (data.name_error) {
				$('#errorAlert-pname').text(data.name_error).show();
			}
			else{
				$('#errorAlert-pname').text(data.name_error).hide();
			}

        
            if (data.gen_error) {
				$('#errorAlert-gender').text(data.gen_error).show();
			}
			else{
				$('#errorAlert-gender').text(data.gen_error).hide();
			}

			if (data.age_error) {
				$('#errorAlert-age').text(data.age_error).show();
			}
			else{
				$('#errorAlert-age').text(data.age_error).hide();
			}
			
			
			
		});

		

		event.preventDefault();

	});

});