"use strict";

/* Show an HTML element */
var showElements = function showElements() {
  for (var _len = arguments.length, elements = Array(_len), _key = 0; _key < _len; _key++) {
    elements[_key] = arguments[_key];
  }

  for (var i = 0; i < elements.length; i++) {
    if (elements[i]) {
      elements[i].classList.remove("hide");
    }
  }
};

/* Hide an HTML element */
var hideElements = function hideElements() {
  for (var _len2 = arguments.length, elements = Array(_len2), _key2 = 0; _key2 < _len2; _key2++) {
    elements[_key2] = arguments[_key2];
  }

  for (var i = 0; i < elements.length; i++) {
    if (elements[i]) {
      elements[i].classList.add("hide");
    }
  }
};

/* Returns true if user is on MS Internet Explorer */
function isIE() {
  var ua = navigator.userAgent;
  /* MSIE used to detect old browsers and Trident used to newer ones*/
  var is_ie = ua.indexOf("MSIE ") > -1 || ua.indexOf("Trident/") > -1;
  return is_ie;
}

/* Initialize error text for uploading applicantions */
/* NOTE: Why is this here? */
window.addEventListener("DOMContentLoaded", function () {
  if (document.getElementById("upload-applications-form")) {
    document.getElementById("upload-applications-form").addEventListener("submit", function () {
      showElements(document.getElementById("upload-applications-uploading-text"));
    });
  }
  if (document.getElementById("upload-applications-error-text")) {
    hideElements(document.getElementById("upload-applications-uploading-text"));
  }
});