const requirementAbbreviations = document.getElementsByClassName("requirement-abbreviation");
const requirementTips = document.getElementsByClassName("tooltiptext");
const questionPreviews = document.getElementsByClassName("question-preview");
const questionPreviewDivs = document.getElementsByClassName("question-preview-div");
const shortQuestionTexts = document.getElementsByClassName("short-question-text");
const questionIcons = document.getElementsByClassName("question-icons");
const extractPreviews = document.getElementsByClassName("extract-previews");
const questionAnswerFull = document.getElementsByClassName("question-answer-full");

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
  requirementAbbreviations[i].addEventListener('transitionend', () => {
    requirementAbbreviations[i].classList.add("no-truncation");
  });
};

const contractRequirementTip = function(i) {
  requirementAbbreviations[i].innerText = abbreviations[i];
  requirementAbbreviations[i].addEventListener('transitionend', () => {
    requirementAbbreviations[i].classList.remove("no-truncation");
  });
};

window.addEventListener('DOMContentLoaded', (event) => {

  for (let i = 0; i < requirementAbbreviations.length; i++) {
    initializeText(i);

    requirementAbbreviations[i].addEventListener("mouseover", () => {
      expandRequirementTip(i);
      shortQuestionTexts[i].classList.add("hide");
    });

    requirementAbbreviations[i].addEventListener("mouseleave", () => {
      contractRequirementTip(i);
      shortQuestionTexts[i].classList.remove("hide");
    });

    for (let i = 0; i < questionPreviews.length; i++) {
      questionPreviews[i].addEventListener("click", () => {
        questionAnswerFull[i].classList.contains("row-closed") ? questionAnswerFull[i].classList.remove("row-closed") : questionAnswerFull[i].classList.add("row-closed");
      });

      questionIcons[i].addEventListener("mouseover", () => {
        extractPreviews[i].classList.add("extract-previews-open");
        questionIcons[i].style.fontSize = "3rem";
        if (requirementAbbreviations[i]) {
          requirementAbbreviations[i].classList.add("hide");
        }
      });

      questionPreviews[i].addEventListener("mouseleave", () => {
        extractPreviews[i].classList.remove("extract-previews-open");
        questionIcons[i].style.fontSize = "1.8rem";
        if (requirementAbbreviations[i]) {
          requirementAbbreviations[i].classList.remove("hide");
        }
      });
    }
  }
});
