function post_to_url(path, state, mac, method) {
    method = method || "post"; // Set method to post by default if not specified.

    // The rest of this code assumes you are not using a library.
    // It can be made less wordy if you use one.
    var form = document.createElement("form");
    form.setAttribute("method", method);
    form.setAttribute("action", path);

    var hiddenField = document.createElement("input");
    hiddenField.setAttribute("type", "hidden");
    hiddenField.setAttribute("name", "state");
    hiddenField.setAttribute("value", state);
    hiddenField.setAttribute("name", "mac");
    hiddenField.setAttribute("value", mac); 

    form.appendChild(hiddenField);

    document.body.appendChild(form);

    //foo = path + state + mac + method
    //alert(foo);

    form.submit();
    
}



function get_to_url(path, state, mac) {

    theUrl = path + "/?mac=" + mac + "&state=" + state

    xmlHttp = new XMLHttpRequest();
    xmlHttp.open( "GET", theUrl, false );
    xmlHttp.send( null );
    return xmlHttp.responseText;
      
}


