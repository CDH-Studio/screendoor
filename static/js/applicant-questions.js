const requirementAbbreviations = document.getElementsByClassName("requirement-abbreviation");
const requirementTips = document.getElementsByClassName("tooltiptext");
let abbreviations = [];
let descriptions = [];

const initializeText = function(i) {
  abbreviations[i] = requirementAbbreviations[i].innerText;
  descriptions[i] = requirementTips[i].value;
};

const expandRequirementTip = function(i) {
  const descriptionChars = descriptions[i].split();

  for (let j = 0; j < descriptionChars.length; j++) {
    requirementAbbreviations[i].innerText += descriptionChars[j];
  }
};

const contractRequirementTip = function(i) {
  requirementAbbreviations[i].innerText = abbreviations[i];
};


window.addEventListener('DOMContentLoaded', (event) => {

  for (let i = 0; i < requirementAbbreviations.length; i++) {
    initializeText(i);

    requirementAbbreviations[i].addEventListener("mouseover", () => {
      expandRequirementTip(i);
    });

    requirementAbbreviations[i].addEventListener("mouseleave", () => {
      contractRequirementTip(i);
    });
  }
});
