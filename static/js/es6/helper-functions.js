/* Show an HTML element */
const showElements = function(...elements) {
  for (let i = 0; i < elements.length; i++) {
    if (elements[i]) {
      elements[i].classList.remove("hide");
    }
  }
};

/* Hide an HTML element */
const hideElements = function(...elements) {
  for (let i = 0; i < elements.length; i++) {
    if (elements[i]) {
      elements[i].classList.add("hide");
    }
  }
};

function isIE() {
  var ua = navigator.userAgent;
  /* MSIE used to detect old browsers and Trident used to newer ones*/
  var is_ie = ua.indexOf("MSIE ") > -1 || ua.indexOf("Trident/") > -1;
  
  return is_ie; 
}