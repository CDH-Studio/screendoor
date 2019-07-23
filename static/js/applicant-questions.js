const applicantResponseFull = document.getElementsByClassName("applicant-response-full");

const extractPreviews = document.getElementsByClassName("extract-previews");

const extractFull = document.getElementsByClassName("extracts-full");

const requirementAbbreviations = document.getElementsByClassName("requirement-abbreviation");
const requirementTips = document.getElementsByClassName("tooltiptext");

const questionPreviews = document.getElementsByClassName("question-preview");
const questionPreviewDivs = document.getElementsByClassName("question-preview-div");

const addNoteIcons = document.getElementsByClassName("add-note");

const shortQuestionTexts = document.getElementsByClassName("short-question-text");

const questionIcons = document.getElementsByClassName("question-icon-div");

const questionAnswerFull = document.getElementsByClassName("question-answer-full");

const educationHeaders = document.getElementsByClassName("education-header");

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

const untruncateEducationHeader = function(i) {
  for (let j = 1; j < educationHeaders[i].getElementsByTagName("div").length; j++) {
    educationHeaders[i].getElementsByTagName("div")[j].classList.remove("truncation");

  }
};

const truncateEducationHeader = function(i) {
  for (let j = 1; j < educationHeaders[i].getElementsByTagName("div").length; j++) {
    educationHeaders[i].getElementsByTagName("div")[j].classList.add("truncation");
  }
};

const expandEducationHeaders = function(i) {
  if (hiddenEducationInfo[i].classList.contains("row-closed")) {
    hiddenEducationInfo[i].classList.remove("row-closed");
  } else {
    hiddenEducationInfo[i].classList.add("row-closed");
  }
};

const hiddenEducationInfo = document.getElementsByClassName("hidden-education-info");

const openCloseQuestionFull = function(i) {
  if (addNoteIcons[i].classList.contains("hide")) {
    applicantResponseFull[i].classList.add("applicant-response-full-open");
    extractFull[i].classList.add("extracts-full-open");

    for (let j = 0; j < extractFull[i].getElementsByTagName("i").length; j++) {
      extractFull[i].getElementsByTagName("i")[j].classList.remove("hide");
    }

    questionAnswerFull[i].classList.remove("row-closed");
    addNoteIcons[i].classList.remove("hide");
    questionIcons[i].classList.add("hide");
  } else {
    applicantResponseFull[i].classList.remove("applicant-response-full-open");
    extractFull[i].classList.remove("extracts-full-open");

    for (let j = 0; j < extractFull[i].getElementsByTagName("i").length; j++) {
      extractFull[i].getElementsByTagName("i")[j].classList.add("hide");
    }

    addNoteIcons[i].classList.add("hide");
    questionIcons[i].classList.remove("hide");
    questionAnswerFull[i].classList.add("row-closed");
  }
};

window.addEventListener('DOMContentLoaded', (event) => {

  for (let i = 0; i < questionPreviews.length; i++) {
    questionPreviewDivs[i].addEventListener("click", () => {
      openCloseQuestionFull(i);
    });
  }

  for (let i = 0; i < educationHeaders.length; i++) {
    educationHeaders[i].addEventListener("click", () => {
      expandEducationHeaders(i);
    });

    educationHeaders[i].addEventListener("mouseover", () => {
      untruncateEducationHeader(i);
    });

    educationHeaders[i].addEventListener('mouseleave', () => {
      truncateEducationHeader(i);
    });
  }

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

    let offsets = [];
    let scrollWidths = [];

    for (let i = 0; i < questionPreviews.length; i++) {
      offsets[i] = shortQuestionTexts[i].offsetWidth;
      scrollWidths[i] = shortQuestionTexts[i].scrollWidth;

      shortQuestionTexts[i].addEventListener("mouseover", () => {
        if (offsets[i] < scrollWidths[i]) {
          extractPreviews[i].classList.add("extract-extra-margin");
        }
      });

      shortQuestionTexts[i].addEventListener("mouseleave", () => {
        extractPreviews[i].classList.remove("extract-extra-margin");
      });

      questionPreviewDivs[i].addEventListener("click", () => {
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
