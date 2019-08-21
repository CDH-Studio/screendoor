/* li elements for each requirement types */
const requirementTypes = document.getElementsByClassName("requirement-type");

/* Divs corresponding to the hidden area with each requirement contained within */
const hiddenRequirementSections = document.getElementsByClassName("hidden-requirement-info");

/* Icons indicating that each requirement can be expanded */
const expandRequirementButtons = document.getElementsByClassName("expand-requirement");

/* Button to expand all requirement sections  */
const expandAllRequirementsButton = document.getElementById("expand-collapse-criteria");

/* Expand all collapsed requirement sections */
const expandAllRequirements = function() {
  expandAllRequirementsButton.innerText = "unfold_less";
  for (let i = 0; i < hiddenRequirementSections.length; i++) {
    expandRequirement(i);
  }
};

/* Close all requirement sections */
const collapseAllRequirements = function() {
  expandAllRequirementsButton.innerText = "unfold_more";
  for (let i = 0; i < hiddenRequirementSections.length; i++) {
    collapseRequirement(i);
  }
};

/* Expand or collapse all requirements, depending if they are open or not */
const expandCollapseAllRequirements = function() {
  if (expandAllRequirementsButton.innerText == "unfold_more") {
    expandAllRequirements();
  } else {
    collapseAllRequirements();
  }
};

/* Expand a specific requirement row */
const expandRequirement = function(i) {
  expandRequirementButtons[i].innerText = "expand_less";
  hiddenRequirementSections[i].classList.remove("row-closed");
  requirementTypes[i].classList.remove("hoverable");
};


/* Collapse a specific requirement row */
const collapseRequirement = function(i) {
  expandRequirementButtons[i].innerText = "expand_more";
  hiddenRequirementSections[i].classList.add("row-closed");
  requirementTypes[i].classList.add("hoverable");
};

/* Expand or collapse a specifc requirement section depending on if it is open or closed */
const expandCollapseRequirement = function(i) {
  hiddenRequirementSections[i].classList.contains("row-closed") ? expandRequirement(i) : collapseRequirement(i);
};

/* List of listeners to allow for removal of listeners */
let listenerList = [];

/* Initialize requirement listeners */
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

/* Remove requirement listeners (NOTE: used in editing script) */
const removeRequirementListeners = function() {
  for (let i = 0; i < requirementTypes.length; i++) {
    const expandCollapseListener = listenerList[i];
    requirementTypes[i].removeEventListener("click", expandCollapseListener);
    requirementTypes[i].style.cursor = "default";
  }
};

/* Initialize listeners */
window.addEventListener("DOMContentLoaded", () => {
  addRequirementListeners();

  expandAllRequirementsButton.addEventListener("click", () => {
    expandCollapseAllRequirements();
  });
});
