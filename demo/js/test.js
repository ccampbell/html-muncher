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
    $.qs(".dont_know", class_thing).value;
    var cool = $.qs("#one_id.class_thing", test);
    var another_weird_thing = $.qs(".class1.class2 #another_id");
    $.qs(".selector1 > .selector2 .selector3");
    var test = document.querySelector(".selector1");
}
