

jquery = require('jquery');


/* ===========================================================================
 *	    Function to copy new URL to clipboard
 * =========================================================================*/
jquery(document).ready(function() {
    jquery('[id^="clipboard_btn-"]').click( function() {
        
        // get redirect url
        var redir_url = this.id.split(/-(.+)/)[1];
       
        console.log(redir_url);
        // create temporary element and grab its text area
        var textArea = document.createElement("textarea");
        textArea.value = jquery('#clipboard-'+redir_url).text();
        console.log(textArea.value);
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand("Copy");

        // remove temp element
        textArea.remove();
    });
});

/* ===========================================================================
 *	    TOGGLE - enable/disable requested URL suffix entry
 * =========================================================================*/
jquery(document).ready( function() {
    jquery("input[name=request_url_suffix_true]").on( "change", function() {
        if(document.getElementById('request_url_suffix_true').checked) {
            console.log('requesting');
            jquery('#request_url_suffix').attr('disabled',false);
            //jquery('.new_delivery_location_line').show();
            //jquery('.existing_delivery_location_line').hide();
        }
        else {
            console.log('NOT requesting');
            jquery('#request_url_suffix').attr('disabled',true);
            //jquery('.new_delivery_location_line').hide();
            //jquery('.existing_delivery_location_line').show();
        }
    });
    jquery('#request_url_suffix_true').trigger('change');
});


