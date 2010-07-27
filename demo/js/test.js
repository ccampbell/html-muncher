$ = {
    qs: function(query) {
        return document.querySelector(query);
    }
};

window.onload = function() 
{
    $.qs("#special").innerHTML = "new text for this paragraph";
}
