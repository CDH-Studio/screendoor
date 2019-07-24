/* CONSTANTS AND VARIABLES */

const favourites = document.getElementsByClassName("favourited");
const not_favourites = document.getElementsByClassName("not_favourited");

const unfavourite = function(i, id) {
  console.log(id)
};

const favourite = function(i, id) {
  console.log(id)
  var opts = {
    method: 'GET',
    headers: {}
  };
  fetch('/add_to_favorites', opts).then(function (response) {return response.json();})
    .then(function (body) {
        alert("afdluibDVGIOJASD")
    });
};

window.addEventListener('DOMContentLoaded', (event) => {
  for (let i = 0; i < favourites.length; i++) {
    console.log()
    favourites[i].addEventListener("click", () => {
      unfavourite(i, favourites[i].id);
    });
  }

  for (let i = 0; i < not_favourites.length; i++) {

    not_favourites[i].addEventListener("click", () => {
      favourite(i, not_favourites[i].id);
    });
  }

});
