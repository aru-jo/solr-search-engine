$(document).ready(function() {

	$("#query").bind("keyup", function() { 

			var dict = {'d': $('#query').val()}

			$.ajax({
				type :'POST',
				url: '/autocomplete',
				data: JSON.stringify(dict),
				contentType: 'application/json'
			})
			.done(function(fill){

				if($('#suggest').length)
				{
					console.log('remove');
					$('#suggest').remove();
				}
								
				var suggestions = fill.sug 

				var disp_string = ''
				
				var addition = '<datalist id = "suggest"' + '>'
				
				for (var i = 0; i < suggestions.length; ++i)
				{
					var row = suggestions[i];
					var appender = ''; 
					for (var j = 0; j < row.length; ++ j)
					{	
						appender += row[j] + ' '; 
					}
					addition += '<option>'+appender+'</option>';
					appender += '...'; 
					disp_string += appender; 
				}

				addition += '</datalist>'
				$(addition).appendTo('#suggest-list');
				$('#disp').text(disp_string).show();
				console.log(addition);
			});
	});

	$('form').on('submit', function(event) {

		$.ajax({
			data : {
				query : $('#query').val(),
				radio : $('input[name=option]:checked').val()

			},
			type : 'POST',
			url : '/process'
		})
		.done(function(dataret) {

			if($('#res-tab'))
			{
				$('#res-tab').remove();
			}

		var doc = "Documents found: "+ dataret.n

		$('#nodocs').text(doc).show();

		console.log(dataret.c)

		if(dataret.c == 1){
			console.log('Spell SAME')
			console.log(dataret.c)
			var reply = "Spell Check is same as query"
			$('#replydisp').text(reply).show();
		}
		else{
			var reply = "Did you mean: " + dataret.c
			console.log(dataret.c)
			$('#spelldisp').text(reply).show();
		
		}

		var table = '<table class = "table table-bordered" id ="res-tab"><tbody>'

		object = dataret.lst
		no_of_rows = object.length

		for(var i = 0 ; i < no_of_rows; ++i)
		{
			table += '<tr>';
			table += '<td>'; 
			row = object[i]
			console.log(row[i])

			for (var j=0 ; j < 2; ++j)
			{
				table += "<a href='"+row[0]+"'>"+row[j]+"</a>"+'<br>';
			}
			for (var k = 2; k < 4; ++k)
			{
				table += row[k] + '<br>'
			}


			table += '</td>'; 

			table += '</tr>';

		}
		
		table += '</tbody></table>';

		console.log(table)

		$(table).appendTo('#table-div');

		});

		event.preventDefault();

	});
});
