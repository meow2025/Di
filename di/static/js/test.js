function check_notifications() {
    $.get("/notification/count", function(data, status) {
        if(status == "success") {
            if(data != "0") {
                $("#notification").text("Notification" + "(" + data + ")");
            }
            else {
                $("#notification").text("Notification");
            }
        }
    })
}

function convert_timestamp_to_date(timestamp, precise) {
    var d = new Date(timestamp);
    if(precise)
    {
        return d.getFullYear() + "/" + d.getMonth() + "/" + d.getDay() + " " + 
               d.getHours() + ":" + d.getMinutes();
    }
    else
    {
        var now = new Date();
        if(now.getFullYear() != d.getFullYear())
            return now.getFullYear() - d.getFullYear() + "y ago"
        else if(now.getMonth() != d.getMonth())
            return now.getMonth() - d.getMonth() + "m ago"
        else if(now.getDay() != d.getDay())
            return now.getDay() - d.getDay() + "d ago"
        else if(now.getHours() != d.getHours())
            return now.getHours() - d.getHours() + "h ago"
        else if(now.getMinutes() != d.getMinutes())
            return now.getMinutes() - d.getMinutes() + "m ago"
        else
            return "just now"
    }
}

function refresh_time() {
    $("[timestamp]").each(function(index) {
        timestamp = $(this).attr("timestamp") * 1000;
        precise = $(this).attr("precise")
        $(this).text(convert_timestamp_to_date(timestamp, precise));
    })
}

function reply(username) {
    $("textarea").focus()
    $("textarea").val($("textarea").val() + "@" + username);
}

$("document").ready(function() {
    if ($("#notification").length) {
        check_notifications();
        setInterval(check_notifications, 10000);
    }
    refresh_time()
    setInterval(refresh_time, 60000);
})
