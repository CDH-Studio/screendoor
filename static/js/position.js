/* CONSTANTS AND VARIABLES */

const favourites = document.getElementsByClassName("favourite-icon");

const unfavourite = function(i, id) {
  console.log(id);
};

const favourite = function(i, id) {
  url = "/add_to_favourites?app_id=" + id + "&favouriteStatus=" + document.getElementById(id).dataset.favouriteStatus;
  fetch(url).then(function(response) {
    /* data being the json object returned from Django function */
    response.json().then(function(data) {
      element = document.getElementById(id); // the outer span surrounding the icon
      if (data.favourite_status == "True") {
        element.children[0].innerText = 'star_border';
        element.setAttribute("data-favourite-status", "False");
      } else {
        element.children[0].innerText = 'star';
        element.setAttribute("data-favourite-status", "True");
      }
    }).catch(error => console.error());
  });
};


const setDefaultFavouriteStatus = function(element) {
  const favouriteStatus = element.dataset.favouriteStatus;
  if (favouriteStatus == "False") {
    element.children[0].innerText = 'star_border';
  } else {
    element.children[0].innerText = 'star';
  }
};

window.addEventListener('DOMContentLoaded', (event) => {
  for (let i = 0; i < favourites.length; i++) {
    setDefaultFavouriteStatus(favourites[i]);
    favourites[i].addEventListener("click", () => {
      favourite(i, favourites[i].id);
    });
  }

});
