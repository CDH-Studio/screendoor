/* CONSTANTS AND VARIABLES */

const favourites = document.getElementsByClassName("favourite_icon");

const unfavourite = function(i, id) {
  console.log(id)
};

const favourite = function(i, id) {
  url = "/add_to_favorites?app_id=" + id + "&favouriteStatus=" + document.getElementById(id).dataset.favouriteStatus
  fetch(url).then(function(response) {
    /* data being the json object returned from Django function */
    response.json().then(function(data) {
        console.log(data)
        element = document.getElementById(id) // the outer span surrounding the icon
        if (data.favourite_status == "True") {
            element.innerHTML = '<i class="material-icons grey-text">star_border</i>'
             element.setAttribute("data-favourite-status", "False")
        } else {
            element.innerHTML = '<i class="material-icons yellow-text">star</i>'
             element.setAttribute("data-favourite-status", "True")
        }
//        console.log(element.parentNode.parentNode.parentNode.parentNode.parentNode)
//        console.log(element.parentNode.parentNode.parentNode.parentNode.parentNode.parentNode)
//        element.parentNode.parentNode.parentNode.parentNode.parentNode.parentNode.appendChild(element.parentNode.parentNode.parentNode.parentNode.parentNode)
    }).catch(error => console.error());
  });
};


const set_default_favourite_status = function(element) {
    favourite_status = element.dataset.favouriteStatus
    if (favourite_status == "False") {
            element.innerHTML = '<i class="material-icons grey-text">star_border</i>'
        } else {
            element.innerHTML = '<i class="material-icons yellow-text">star</i>'
        }
};

window.addEventListener('DOMContentLoaded', (event) => {
  for (let i = 0; i < favourites.length; i++) {
    set_default_favourite_status(favourites[i])
    favourites[i].addEventListener("click", () => {
      favourite(i, favourites[i].id);
    });
  }

});
