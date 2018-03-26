

$(document).ready(function(e) {
     var s = '#body div[name=left_body] ul';
     $(s).find("li").each(function () {
            var a = $(this).find("a:first")[0];
            if ($(a).attr("href") === location.pathname) {
                $(this).addClass("active");
            } else {
                $(this).removeClass("active");
            }
        });
});

