const favouriteIcons = document.getElementsByClassName("favourite-icon");

const changeFavouriteStatus = function(i, id) {
  const url = "/change_favourites_status?app_id=" + id +
        "&favouriteStatus=" + document.getElementById(id).dataset.favouriteStatus;
  fetch(url).then(function(response) {
    /* data being the json object returned from Django function */
    response.json().then(function(data) {
      const element = document.getElementById(id);
      if (data.favourite_status == "True") {
        element.children[0].innerText = "star_border";
        element.setAttribute("data-favourite-status", "False");
      } else {
        element.children[0].innerText = "star";
        element.setAttribute("data-favourite-status", "True");
      }
    }).catch(() => console.error());
  });
};


const setDefaultFavouriteStatus = function(element) {
  const favouriteStatus = element.dataset.favouriteStatus;
  if (favouriteStatus == "False") {
    element.children[0].innerText = "star_border";
  } else {
    element.children[0].innerText = "star";
  }
};

window.addEventListener("DOMContentLoaded", () => {
  for (let i = 0; i < favouriteIcons.length; i++) {
    setDefaultFavouriteStatus(favouriteIcons[i]);
    favouriteIcons[i].addEventListener("click", () => {
      changeFavouriteStatus(i, favouriteIcons[i].id);
    });
  }
});
