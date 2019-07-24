/* CONSTANTS AND VARIABLES */

const favourites = document.getElementsByClassName("favourited");
const not_favourites = document.getElementsByClassName("not_favourited");

const unfavourite = function(i, id) {
  console.log(id)
};

const favourite = function(i, id) {
  url = "/add_to_favorites?app_id=" + id
  fetch(url).then(function(response) {
    /* data being the json object returned from Django function */
    response.json().then(function(data) {
      document.getElementById(id).innerHTML = '<i class="material-icons yellow-text">star</i>'
    }).catch(error => console.error());
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
