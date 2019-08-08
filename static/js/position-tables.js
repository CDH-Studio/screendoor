"use strict";

var requirementTypes = document.getElementsByClassName("requirement-type");
var hiddenRequirementSections = document.getElementsByClassName("hidden-requirement-info");
var expandRequirementButtons = document.getElementsByClassName("expand-requirement");
var expandAllRequirementsButton = document.getElementById("expand-collapse-criteria");

var expandAllRequirements = function expandAllRequirements() {
  expandAllRequirementsButton.innerText = "unfold_less";
  for (var i = 0; i < hiddenRequirementSections.length; i++) {
    expandRequirement(i);
  }
};

var collapseAllRequirements = function collapseAllRequirements() {
  expandAllRequirementsButton.innerText = "unfold_more";
  for (var i = 0; i < hiddenRequirementSections.length; i++) {
    collapseRequirement(i);
  }
};

var expandCollapseAllRequirements = function expandCollapseAllRequirements() {
  if (expandAllRequirementsButton.innerText == "unfold_more") {
    expandAllRequirements();
  } else {
    collapseAllRequirements();
  }
};

var expandRequirement = function expandRequirement(i) {
  expandRequirementButtons[i].innerText = "expand_less";
  hiddenRequirementSections[i].classList.remove("row-closed");
  requirementTypes[i].classList.remove("hoverable");
};

var collapseRequirement = function collapseRequirement(i) {
  expandRequirementButtons[i].innerText = "expand_more";
  hiddenRequirementSections[i].classList.add("row-closed");
  requirementTypes[i].classList.add("hoverable");
};

var expandCollapseRequirement = function expandCollapseRequirement(i) {
  hiddenRequirementSections[i].classList.contains("row-closed") ? expandRequirement(i) : collapseRequirement(i);
};

var listenerList = [];

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

var removeRequirementListeners = function removeRequirementListeners() {
  for (var i = 0; i < requirementTypes.length; i++) {
    var expandCollapseListener = listenerList[i];
    requirementTypes[i].removeEventListener("click", expandCollapseListener);
    requirementTypes[i].style.cursor = "default";
  }
};

window.addEventListener("DOMContentLoaded", function () {
  addRequirementListeners();

  expandAllRequirementsButton.addEventListener("click", function () {
    expandCollapseAllRequirements();
  });
});