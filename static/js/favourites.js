"use strict";

/* Spans containing favouriting "star" icons */
var favouriteIcons = document.getElementsByClassName("favourite-icon");

/* Change the "favourite" status of an applicant for a user via AJAX */
var changeFavouriteStatus = function changeFavouriteStatus(i, id) {
  var url = "/change_favourites_status?app_id=" + id + "&favouriteStatus=" + document.getElementById(id).dataset.favouriteStatus;
  fetch(url).then(function (response) {
    /* data being the json object returned from Django function */
    response.json().then(function (data) {
      var element = document.getElementById(id);
      if (data.favourite_status == "True") {
        element.children[0].innerText = "star_border";
        element.setAttribute("data-favourite-status", "False");
      } else {
        element.children[0].innerText = "star";
        element.setAttribute("data-favourite-status", "True");
      }
    }).catch(function () {
      return console.error();
    });
  });
};

/* Initialize icons for whether an applicant is favourited or not */
var setDefaultFavouriteStatus = function setDefaultFavouriteStatus(element) {
  var favouriteStatus = element.dataset.favouriteStatus;
  if (favouriteStatus == "False") {
    element.children[0].innerText = "star_border";
  } else {
    element.children[0].innerText = "star";
  }
};

/* Initialize listeners for favouriting applicants */
window.addEventListener("DOMContentLoaded", function () {
  var _loop = function _loop(i) {
    setDefaultFavouriteStatus(favouriteIcons[i]);
    favouriteIcons[i].addEventListener("click", function () {
      changeFavouriteStatus(i, favouriteIcons[i].id);
    });
  };

  for (var i = 0; i < favouriteIcons.length; i++) {
    _loop(i);
  }
});