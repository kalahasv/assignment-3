let searchWord = "";
// Custom implementation of waiting until the user stops typing before calling a setTimeout event from one of my older projects -Tim
let delay = (function () {
    var timer = 0;
    return function (callback, ms, that) {
        clearTimeout(timer);
        timer = setTimeout(callback.bind(that), ms);
    };
})();

function search() {
    console.log("searching");
    while (document.getElementById("searchresults").hasChildNodes()) {
        document.getElementById("searchresults").removeChild(document.getElementById("searchresults").lastChild);
    }
    $.get("/query/" + searchWord, function (data) {
        data.forEach(d => createOption(d));
    });
}

function createOption(d) {
    let option = document.createElement("option");
    option.value = d;
    document.getElementById("searchresults").appendChild(option);
}

$(document).ready(function () {
    $('#searchbar').keyup(function () {
        let inputText = $(this).val();
        delay(function () {
            searchWord = inputText;
            search();
        }, 1000);

    });
});