$ = {
    qs: function(query) {
        return document.querySelector(query);
    }
};

window.onload = function()
{
    $.qs("#special").innerHTML = "new text for this paragraph";
    document.getElementById("special").innerHTML = "change it again";
    var italic = document.getElementsByClassName('italic');

    // mootools
    var test = $('test');
    if (test.hasClass("dont_know")) {
        test.removeClass("dont_know");
        test.addClass('now_i_know');
    }

    var class_thing = $('class_thing');
    class_thing.addClass(test, "whatever");
    class_thing.removeClass(test, "whatever");
}
