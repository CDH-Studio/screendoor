const requirementTypes = document.getElementsByClassName("requirement-type");
const hiddenRequirementSections = document.getElementsByClassName("hidden-requirement-info");
const expandRequirementButtons = document.getElementsByClassName("expand-requirement");
const expandAllRequirementsButton = document.getElementById("expand-collapse-criteria");

const expandAllRequirements = function() {
  expandAllRequirementsButton.innerText = "unfold_less";
  for (let i = 0; i < hiddenRequirementSections.length; i++) {
    expandRequirement(i);
  }
};

const collapseAllRequirements = function() {
  expandAllRequirementsButton.innerText = "unfold_more";
  for (let i = 0; i < hiddenRequirementSections.length; i++) {
    collapseRequirement(i);
  }
};

const expandCollapseAllRequirements = function() {
  if (expandAllRequirementsButton.innerText == "unfold_more") {
    expandAllRequirements();
  } else {
    collapseAllRequirements();
  }
};

const expandRequirement = function(i) {
  expandRequirementButtons[i].innerText = "expand_less";
  hiddenRequirementSections[i].classList.remove("row-closed");
  requirementTypes[i].classList.remove("hoverable");
};

const collapseRequirement = function(i) {
  expandRequirementButtons[i].innerText = "expand_more";
  hiddenRequirementSections[i].classList.add("row-closed");
  requirementTypes[i].classList.add("hoverable");
};

const expandCollapseRequirement = function(i) {
  hiddenRequirementSections[i].classList.contains("row-closed") ? expandRequirement(i) : collapseRequirement(i);
};

let listenerList = [];

const addRequirementListeners = function() {
  listenerList = [];
  for (let i = 0; i < requirementTypes.length; i++) {
    const expandCollapseListener = () => {
      expandCollapseRequirement(i);
    };
    requirementTypes[i].addEventListener("click", expandCollapseListener);
    requirementTypes[i].style.cursor = "pointer";
    listenerList.push(expandCollapseListener);
  }
};

const removeRequirementListeners = function() {
  for (let i = 0; i < requirementTypes.length; i++) {
    const expandCollapseListener = listenerList[i];
    requirementTypes[i].removeEventListener("click", expandCollapseListener);
    requirementTypes[i].style.cursor = "default";
  }
};

window.addEventListener("DOMContentLoaded", () => {
  addRequirementListeners();


  expandAllRequirementsButton.addEventListener("click", () => {
    expandCollapseAllRequirements();
  });
});
