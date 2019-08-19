"use strict";

/* li elements for each requirement types */
var requirementTypes = document.getElementsByClassName("requirement-type");

/* Divs corresponding to the hidden area with each requirement contained within */
var hiddenRequirementSections = document.getElementsByClassName("hidden-requirement-info");

/* Icons indicating that each requirement can be expanded */
var expandRequirementButtons = document.getElementsByClassName("expand-requirement");

/* Button to expand all requirement sections  */
var expandAllRequirementsButton = document.getElementById("expand-collapse-criteria");

/* Expand all collapsed requirement sections */
var expandAllRequirements = function expandAllRequirements() {
  expandAllRequirementsButton.innerText = "unfold_less";
  for (var i = 0; i < hiddenRequirementSections.length; i++) {
    expandRequirement(i);
  }
};

/* Close all requirement sections */
var collapseAllRequirements = function collapseAllRequirements() {
  expandAllRequirementsButton.innerText = "unfold_more";
  for (var i = 0; i < hiddenRequirementSections.length; i++) {
    collapseRequirement(i);
  }
};

/* Expand or collapse all requirements, depending if they are open or not */
var expandCollapseAllRequirements = function expandCollapseAllRequirements() {
  if (expandAllRequirementsButton.innerText == "unfold_more") {
    expandAllRequirements();
  } else {
    collapseAllRequirements();
  }
};

/* Expand a specific requirement row */
var expandRequirement = function expandRequirement(i) {
  expandRequirementButtons[i].innerText = "expand_less";
  hiddenRequirementSections[i].classList.remove("row-closed");
  requirementTypes[i].classList.remove("hoverable");
};

/* Collapse a specific requirement row */
var collapseRequirement = function collapseRequirement(i) {
  expandRequirementButtons[i].innerText = "expand_more";
  hiddenRequirementSections[i].classList.add("row-closed");
  requirementTypes[i].classList.add("hoverable");
};

/* Expand or collapse a specifc requirement section depending on if it is open or closed */
var expandCollapseRequirement = function expandCollapseRequirement(i) {
  hiddenRequirementSections[i].classList.contains("row-closed") ? expandRequirement(i) : collapseRequirement(i);
};

/* List of listeners to allow for removal of listeners */
var listenerList = [];

/* Initialize requirement listeners */
var addRequirementListeners = function addRequirementListeners() {
  listenerList = [];

  var _loop = function _loop(i) {
    var expandCollapseListener = function expandCollapseListener() {
      expandCollapseRequirement(i);
    };
    requirementTypes[i].addEventListener("click", expandCollapseListener);
    requirementTypes[i].style.cursor = "pointer";
    listenerList.push(expandCollapseListener);
  };

  for (var i = 0; i < requirementTypes.length; i++) {
    _loop(i);
  }
};

/* Remove requirement listeners (NOTE: used in editing script) */
var removeRequirementListeners = function removeRequirementListeners() {
  for (var i = 0; i < requirementTypes.length; i++) {
    var expandCollapseListener = listenerList[i];
    requirementTypes[i].removeEventListener("click", expandCollapseListener);
    requirementTypes[i].style.cursor = "default";
  }
};

/* Initialize listeners */
window.addEventListener("DOMContentLoaded", function () {
  addRequirementListeners();

  expandAllRequirementsButton.addEventListener("click", function () {
    expandCollapseAllRequirements();
  });
});