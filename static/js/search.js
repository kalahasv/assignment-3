let searchWord = "";
// Custom implementation of waiting until the user stops typing before calling a setTimeout event from one of my older projects -Tim
let delay = (() => {
    var timer = 0;
    return (callback, ms, that) => {
        clearTimeout(timer);
        timer = setTimeout(callback.bind(that), ms);
    };
})();

function search() {
    console.log("searching");
    while (document.getElementById("searchresults").hasChildNodes()) {
        document.getElementById("searchresults").removeChild(document.getElementById("searchresults").lastChild);
    }
    $.get("/query/" + searchWord, (data) => {
        data.forEach(d => createOption(d));
    });
}

function createOption(d) {
    let option = document.createElement("option");
    option.value = d;
    document.getElementById("searchresults").appendChild(option);
}

$(document).ready(() => {
    $('#searchbar').keyup(() => {
        let inputText = $(this).val();
        delay(() => {
            searchWord = inputText;
            search();
        }, 1000);

    });
});