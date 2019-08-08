"use strict";

/* CONSTANTS AND VARIABLES */

/* Collapsible table elements */
var collapseElements = document.getElementsByClassName("collapse");
var collapseArrows = document.getElementsByClassName("collapse-arrows");

/* Buttons */
var collapseAllButton = document.getElementById("collapse-all");
var expandAllButton = document.getElementById("expand-all");

/* Ellipses */
var questionEllipses = document.getElementsByClassName("question-ellipsis");
var questionHeaders = document.getElementsByClassName("question-header");
var questionSubheads = document.getElementsByClassName("question-subhead");

/* Analysis preview and full */
var analysisSpan = document.getElementsByClassName("analysis-preview");
var questionSpan = document.getElementsByClassName("question-preview");
var questionTruncated = [];
var questionTruncatedAnalysis = [];
var analysisSubheads = [];
var previewFull = [];
var previewSmall = [];
var clickedHeaders = [];

/* Education preview */
var educationEllipses = document.getElementsByClassName("education-ellipsis");
// const educationHeaders = document.getElementsByClassName("education-header");
var educationHeadersClicked = document.getElementsByClassName("education-header-clicked");
var educationAcademicTruncated = [];
var educationInstitutionTruncated = [];
var educationAreaStudyTruncated = [];

/* HELPER FUNCTIONS */

var slideCloseElements = function slideCloseElements() {
  for (var _len = arguments.length, elements = Array(_len), _key = 0; _key < _len; _key++) {
    elements[_key] = arguments[_key];
  }

  var _iteratorNormalCompletion = true;
  var _didIteratorError = false;
  var _iteratorError = undefined;

  try {
    for (var _iterator = elements[Symbol.iterator](), _step; !(_iteratorNormalCompletion = (_step = _iterator.next()).done); _iteratorNormalCompletion = true) {
      var element = _step.value;

      if (element) {
        element.classList.add("row-closed");
        // element.ontransitionend = () => {
        //   element.classList.add("invisible");
        // };
      }
    }
  } catch (err) {
    _didIteratorError = true;
    _iteratorError = err;
  } finally {
    try {
      if (!_iteratorNormalCompletion && _iterator.return) {
        _iterator.return();
      }
    } finally {
      if (_didIteratorError) {
        throw _iteratorError;
      }
    }
  }
};

var slideOpenElements = function slideOpenElements() {
  for (var _len2 = arguments.length, elements = Array(_len2), _key2 = 0; _key2 < _len2; _key2++) {
    elements[_key2] = arguments[_key2];
  }

  var _iteratorNormalCompletion2 = true;
  var _didIteratorError2 = false;
  var _iteratorError2 = undefined;

  try {
    for (var _iterator2 = elements[Symbol.iterator](), _step2; !(_iteratorNormalCompletion2 = (_step2 = _iterator2.next()).done); _iteratorNormalCompletion2 = true) {
      var element = _step2.value;

      if (element) {
        element.classList.remove("row-closed");
        // element.classList.remove("invisible");
        // element.ontransitionend = () => {
        //   element.classList.remove("invisible");
        // };
      }
    }
  } catch (err) {
    _didIteratorError2 = true;
    _iteratorError2 = err;
  } finally {
    try {
      if (!_iteratorNormalCompletion2 && _iterator2.return) {
        _iterator2.return();
      }
    } finally {
      if (_didIteratorError2) {
        throw _iteratorError2;
      }
    }
  }
};

/* Toggles TBODY collapse and expand */
var toggleRow = function toggleRow(row) {
  if (row) {
    row.classList.contains("row-closed") ? slideOpenElements(row) : slideCloseElements(row);
    try {
      if (row.nextElementSibling.classList.contains("body-row")) {
        row = row.nextElementSibling;
        toggleRow(row);
      }
    } catch (TypeError) {}
  }
};

/* Display ellipses if there is truncated text on row */
var displayEllipsesIfNeeded = function displayEllipsesIfNeeded(i) {
  !isEllipsisActive(questionTruncated[i], questionTruncatedAnalysis[i]) ? slideCloseElements(questionEllipses[i]) : slideOpenElements(questionEllipses[i]);
};

/* Arrow indicates row is open or closed */
var openCloseArrow = function openCloseArrow(i) {
  if (collapseArrows[i]) {
    collapseArrows[i].innerHTML == "keyboard_arrow_right" ? collapseArrows[i].innerHTML = "keyboard_arrow_down" : collapseArrows[i].innerHTML = "keyboard_arrow_right";
  }
};

/* User wants to view question detail */
var expandCollapseQuestionHeaders = function expandCollapseQuestionHeaders(i) {
  !isOpen(previewSmall[i]) ? expandQuestionHeaders(i) : collapseQuestionHeaders(i);
};

var expandQuestionHeaders = function expandQuestionHeaders(i) {
  slideOpenElements(clickedHeaders[i]);
  slideCloseElements(previewFull[i], previewSmall[i]);
  // backgroundOffWhite(questionHeaders[i]);
};

var collapseQuestionHeaders = function collapseQuestionHeaders(i) {
  slideOpenElements(previewSmall[i]);
  slideCloseElements(clickedHeaders[i]);
  // backgroundWhite(questionHeaders[i]);
  hideQuestionPreview(i);
};

/* User moves mouse over question ellipses */
var showQuestionPreview = function showQuestionPreview(i) {
  slideCloseElements(analysisSpan[i], questionSpan[i]);
  slideOpenElements(previewFull[i], questionSubheads[i]);
  // backgroundOffWhite(previewSmall[i]);
  unTruncate(questionTruncated[i]);
  growEllipsis(questionEllipses[i]);

  if (analysisSubheads[i]) {
    slideOpenElements(analysisSubheads[i]);
  }
  if (questionTruncatedAnalysis[i]) {
    unTruncate(questionTruncatedAnalysis[i]);
  }
};

/* User moves mouse off question preview */
var hideQuestionPreview = function hideQuestionPreview(i) {
  slideOpenElements(analysisSpan[i], questionSpan[i]);
  slideCloseElements(questionSubheads[i], previewFull[i]);
  // backgroundWhite(previewSmall[i]);
  truncate(questionTruncated[i]);
  shrinkEllipsis(questionEllipses[i]);

  if (analysisSubheads[i]) {
    slideCloseElements(analysisSubheads[i]);
  }
  if (questionTruncatedAnalysis[i]) {
    truncate(questionTruncatedAnalysis[i]);
  }
};

/* User clicks an education row */
var showEducationFull = function showEducationFull(i) {
  showElements(educationHeadersClicked[i]);
  slideOpenElements(educationHeadersClicked[i]);
  hideElements(educationHeaders[i]);
  slideCloseElements(educationHeaders[i]);
};

/* User clicks an expanded education row */
var hideEducationFull = function hideEducationFull(i) {
  hideElements(educationHeadersClicked[i]);
  slideCloseElements(educationHeadersClicked[i]);
  showElements(educationHeaders[i]);
  slideOpenElements(educationHeaders[i]);
};

/* User moves mouse over education ellipses */
var showEducationPreview = function showEducationPreview(i) {
  if (isEllipsisActive(educationAreaStudyTruncated[i], educationInstitutionTruncated[i], educationAcademicTruncated[i])) {
    growEllipsis(educationEllipses[i]);
  }
  // backgroundOffWhite(educationHeaders[i]);
  unTruncate(educationAcademicTruncated[i], educationInstitutionTruncated[i], educationAreaStudyTruncated[i]);
};

/* User moves mouse off education preview */
var hideEducationPreview = function hideEducationPreview(i) {
  // backgroundWhite(educationHeaders[i]);
  shrinkEllipsis(educationEllipses[i]);
  truncate(educationAcademicTruncated[i], educationAreaStudyTruncated[i], educationInstitutionTruncated[i]);
};

/* Row is currently expanded */
var isOpen = function isOpen(row) {
  return !row.classList.contains("row-closed");
};

/* Recursively expands successive TBODY rows */
var expandRow = function expandRow(row) {
  row.classList.remove("row-closed");
  try {
    if (row.nextElementSibling.classList.contains("body-row")) {
      row = row.nextElementSibling;
      expandRow(row);
    }
  } catch (TypeError) {}
};

/* Recursively collapses successive TBODY rows */
var collapseRow = function collapseRow(row) {
  if (row) {
    row.classList.add("row-closed");
    try {
      if (row.nextElementSibling.classList.contains("body-row")) {
        row = row.nextElementSibling;
        collapseRow(row);
      }
    } catch (TypeError) {}
  }
};

/* Toggles TBODY collapse and expand */
var expandOrCollapseRows = function expandOrCollapseRows(row) {
  row.classList.contains("row-closed") ? row.classList.remove("row-closed") : row.classList.add("row-closed");
  try {
    if (row.nextElementSibling.classList.contains("body-row")) {
      row = row.nextElementSibling;
      expandOrCollapseRows(row);
    }
  } catch (TypeError) {}
};

/* Collapse all rows */
var collapseAll = function collapseAll() {
  for (var i = 0; i < collapseElements.length; i++) {
    var row = collapseElements[i].nextElementSibling;
    collapseArrows[i].innerHTML = "keyboard_arrow_right";
    collapseRow(row);
  }

  for (var _i = 0; _i < questionHeaders.length; _i++) {
    collapseQuestionHeaders(_i);
  }

  for (var _i2 = 0; _i2 < questionHeaders.length; _i2++) {
    hideEducationFull(_i2);
  }
};

/* Expand all rows */
var expandAll = function expandAll() {
  for (var i = 0; i < collapseElements.length; i++) {
    var row = collapseElements[i].nextElementSibling;
    collapseArrows[i].innerHTML = "keyboard_arrow_down";
    expandRow(row);
  }

  for (var _i3 = 0; _i3 < questionHeaders.length; _i3++) {
    expandQuestionHeaders(_i3);
  }

  for (var _i4 = 0; _i4 < questionHeaders.length; _i4++) {
    showEducationFull(_i4);
  }
};

/* Truncate the text in an HTML element */
var truncate = function truncate() {
  for (var _len3 = arguments.length, elements = Array(_len3), _key3 = 0; _key3 < _len3; _key3++) {
    elements[_key3] = arguments[_key3];
  }

  elements.forEach(function (element) {
    if (element) {
      element.classList.add("truncation");
      element.classList.remove("truncation-open");
    }
  });
};

/* Un-truncate the text in an HTML element */
var unTruncate = function unTruncate() {
  for (var _len4 = arguments.length, elements = Array(_len4), _key4 = 0; _key4 < _len4; _key4++) {
    elements[_key4] = arguments[_key4];
  }

  elements.forEach(function (element) {
    if (element) {
      element.classList.remove("truncation");
      element.classList.add("truncation-open");
    }
  });
};

/* Indicate that an ellipsis has mouse over it */
var growEllipsis = function growEllipsis(element) {
  element.classList.remove("ellipsis");
  element.classList.add("ellipsis-larger");
};

/* Restore ellipsis to default look */
var shrinkEllipsis = function shrinkEllipsis(element) {
  element.classList.remove("ellipsis-larger");
  element.classList.add("ellipsis");
};

/* Highlight element with off-white background */
var backgroundOffWhite = function backgroundOffWhite(element) {
  element.style.transition = "all .5s ease";
  element.style.backgroundColor = "rgba(242, 242, 242, 0.5)";
};

/* Restore background to white */
var backgroundWhite = function backgroundWhite(element) {
  element.style.backgroundColor = "#ffffff";
};

/* Returns true if the text in an element is truncated */
var isEllipsisActive = function isEllipsisActive() {
  for (var _len5 = arguments.length, elements = Array(_len5), _key5 = 0; _key5 < _len5; _key5++) {
    elements[_key5] = arguments[_key5];
  }

  for (var i = 0; i < elements.length; i++) {
    if (elements[i]) {
      if (elements[i].offsetWidth < elements[i].scrollWidth) {
        return true;
      }
    }
  }
  return false;
};

/* LISTENERS */

/* Individual row click listeners */
var initializeRowListeners = function initializeRowListeners(i) {
  collapseElements[i].style.cursor = 'pointer';
  var row = collapseElements[i].nextElementSibling;

  collapseElements[i].addEventListener("click", function () {
    openCloseArrow(i);
    toggleRow(row);
  });
};

/* Initialize question listeners */
var initializeQuestionListeners = function initializeQuestionListeners() {
  var _loop = function _loop(i) {
    previewFull[i] = document.getElementById("previews-full" + i);
    previewSmall[i] = document.getElementById("previews-small" + i);
    questionTruncated[i] = document.getElementById("truncated" + i);
    questionTruncatedAnalysis[i] = document.getElementById("truncated-analysis" + i);
    analysisSubheads[i] = document.getElementById("analysis-subhead" + i);
    clickedHeaders[i] = document.getElementById("clicked-header" + i);

    slideCloseElements(clickedHeaders[i], previewFull[i]);
    displayEllipsesIfNeeded(i);

    /* User clicks question header */
    questionHeaders[i].addEventListener("click", function () {
      expandCollapseQuestionHeaders(i);
    });

    /* User moves mouse over a question ellipsis */
    questionEllipses[i].addEventListener("mouseover", function () {
      showQuestionPreview(i);
    });

    /* User moves mouse off a question ellipsis */
    questionHeaders[i].addEventListener("mouseleave", function () {
      hideQuestionPreview(i);
    });

    /* Resize adjustment for ellipses */
    window.addEventListener('resize', function () {
      displayEllipsesIfNeeded(i);
    });
  };

  /* Initializes and adds listeners for truncated question text */
  for (var i = 0; i < questionEllipses.length; i++) {
    _loop(i);
  }
};

/* Initializes and creates listeners for education header truncation */
var initializeEducationListeners = function initializeEducationListeners() {
  var _loop2 = function _loop2(i) {
    educationAcademicTruncated[i] = document.getElementById("education-academic-truncated" + i);
    educationInstitutionTruncated[i] = document.getElementById("education-institution-truncated" + i);
    educationAreaStudyTruncated[i] = document.getElementById("education-areastudy-truncated" + i);

    if (!isEllipsisActive(educationAreaStudyTruncated[i], educationInstitutionTruncated[i], educationAcademicTruncated[i])) {
      hideElements(educationEllipses[i]);
    }

    /* User clicks to show education detail */
    educationHeaders[i].addEventListener("click", function () {
      showEducationFull(i);
    });

    /* User clicks to hide education detail */
    educationHeadersClicked[i].addEventListener("click", function () {
      hideEducationFull(i);
    });

    /* User moves mouse over education ellipsis */
    educationEllipses[i].addEventListener("mouseover", function () {
      showEducationPreview(i);
    });

    /* User moves mouse off education ellipsis */
    educationHeaders[i].addEventListener("mouseleave", function () {
      hideEducationPreview(i);
    });

    /* Handles window resizing and adding/removing ellipses based on browser window size */
    window.addEventListener('resize', function () {
      displayEllipsesIfNeeded(i);
    });
  };

  for (var i = 0; i < educationEllipses.length; i++) {
    _loop2(i);
  }
};

/* Initializes positions table with experience and assets collapsed */
window.addEventListener('DOMContentLoaded', function (event) {
  /* Collapse All button listener */
  collapseAllButton.addEventListener("click", collapseAll);

  /* Expand all button listener */
  expandAllButton.addEventListener("click", expandAll);

  for (var i = 0; i < collapseElements.length; i++) {
    initializeRowListeners(i);
    // if (i > (window.location.pathname.includes("application") ? 3 : 2)) {
    //   collapseArrows[i].innerHTML = "keyboard_arrow_right";
    //   collapseRow(collapseElements[i].nextElementSibling);
    // }
  }

  if (window.location.pathname.includes("application")) {
    initializeEducationListeners();
    initializeQuestionListeners();
  }
});