$(document).ready(function () {
    $("#regForm").submit((e) => {
        e.preventDefault();
        console.log($("#regForm").serialize());
        $.post("/register", $("#regForm").serialize())
            .done(function (data) {
                document.getElementById("status").innerHTML = "Success!";
                window.location.replace("/");
            })
            .fail(function(e) {
                console.log(e);
                document.getElementById("status").innerHTML = e.responseText;
            });
    });
});