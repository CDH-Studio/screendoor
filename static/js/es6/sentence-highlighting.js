/* Hidden inputs containing extract string starting indexes */
const extractStringStarts = document.getElementsByClassName("extract-string-index");

/* Hidden inputs containing extract string ending indexes */
const extractStringEnds = document.getElementsByClassName("extract-ending-index");

/* Spans containing the text of each individual extract */
const visibleExtracts = document.getElementsByClassName("extract-text");

/* Divs containing a span containing an individual extract */
const extractDivs = document.getElementsByClassName("extract-full");

/* Hidden inputs containing the id of the parent answer of an extract */
const extractParentAnswerIds = document.getElementsByClassName("extract-parent-answer-id");

/* Hidden inputs containing the parent answer text of the extract */
const extractParentAnswerTexts = document.getElementsByClassName("extract-parent-answer");

/* Spans containing applicant complementary response text */
const answerComplementaryResponse = document.getElementsByClassName("answer-complementary-response");

/* Hidden inputs containing applicant complementary response text */
const answerComplementaryResponseValue = document.getElementsByClassName("answer-complementary-response-value");

/* Underline the extract over which the user is hovering  */
const underlineExtracts = function(extractIndex) {
  visibleExtracts[extractIndex].classList.add("extract-bold");
};


/* Remove underline when user moves mouse away  */
const clearExtractsUnderline = function(extractIndex) {
  visibleExtracts[extractIndex].classList.remove("extract-bold");
};

/* Highlight the sentence corresponding to extract user is hovering */
const highlightSentence = function(extractIndex, answerId) {
  underlineExtracts(extractIndex);

  for (let i = 0; i < answerComplementaryResponse.length; i++) {
    if (answerComplementaryResponse[i].answerId.value == answerId) {

      let startIndex = parseInt(extractStringStarts[extractIndex].value);
      let endIndex = parseInt(extractStringEnds[extractIndex].value);
      const answerText = answerComplementaryResponseValue[i].value;

      const answerBefore = answerText.slice(0, startIndex);
      const answerHighlight = "<span id='answer-highlight' class='answer-highlight'>" + answerText.slice(startIndex, endIndex) + "</span>";
      const answerAfter = answerText.slice(endIndex);

      answerComplementaryResponse[i].innerHTML = answerBefore + answerHighlight + answerAfter;
      document.getElementById("answer-highlight").classList.add("answer-highlighted");
    }
  }
};

/* Remove highlight from sentence */
const unHighlightSentence = function(extractIndex, answerId) {
  clearExtractsUnderline(extractIndex);

  for (let i = 0; i < answerComplementaryResponse.length; i++) {
    if (answerComplementaryResponse[i].answerId.value == answerId) {
      answerComplementaryResponse[i].innerHTML = extractParentAnswerTexts[extractIndex].value;
    }
  }
};

/* Initialize listeners for hovering over extracts */
const setHighlightListeners = function() {
  for (let i = 0; i < visibleExtracts.length; i++) {
    extractDivs[i].addEventListener("mouseover", function() {
      highlightSentence(i, extractParentAnswerIds[i].value);
    });
    extractDivs[i].addEventListener("mouseout", function() {
      unHighlightSentence(i, extractParentAnswerIds[i].value);
    });
  }
  for (let i = 0; i < answerComplementaryResponse.length; i++) {
    answerComplementaryResponse[i].answerId = document.getElementsByClassName("answer-id")[i];
  }
};

window.addEventListener("DOMContentLoaded", setHighlightListeners);
