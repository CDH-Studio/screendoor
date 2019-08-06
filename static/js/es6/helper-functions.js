/* Show an HTML element */
const showElements = function(...elements) {
  for (let element of elements) {
    if (element) {
      element.classList.remove("hide");
    }
  }
};

/* Hide an HTML element */
const hideElements = function(...elements) {
  for (let element of elements) {
    if (element) {
      element.classList.add("hide");
    }
  }
};
