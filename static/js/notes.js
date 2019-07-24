const addNoteButtons = document.getElementsByClassName("add-note");
const addNoteForms = document.getElementsByClassName("note-form");

const deleteNoteButtons = document.getElementsByClassName("delete-note");
const deleteNoteForms = document.getElementsByClassName("delete-note-form");

const cancelNoteButtons = document.getElementsByClassName("cancel-note");

const noteAreas = document.getElementsByClassName("notes-area");
const noteDeleteAnswerCounters = document.getElementsByClassName("note-delete-answer-counter");
const noteInputs = document.getElementsByClassName('note-input');
const noteRows = document.getElementsByClassName("notes-row");
const noteTextArea = document.getElementsByClassName('note-box');

const saveNoteButtons = document.getElementsByClassName("save-note");

const persistOpenedQuestion = function(i) {
  localStorage.setItem('questionIndex', i);
};

const persistOpenedEditBox = function(i) {
  localStorage.setItem('boxOpen', i);
};

const toggleNoteInput = function(i) {
  if (noteTextArea[i].classList.contains("note-box-visible")) {
    noteTextArea[i].classList.remove("note-box-visible");
    addNoteButtons[i].children[0].style.fontSize = "2.1rem";
  } else {
    noteTextArea[i].classList.add("note-box-visible");
    addNoteButtons[i].children[0].style.fontSize = "3rem";
  }
};

const retrieveOpenedQuestion = function() {
  if (localStorage.getItem('questionIndex')) {
    questionPreviewDivs[localStorage.getItem('questionIndex')].click();
    localStorage.removeItem('questionIndex');
  }
  if (localStorage.getItem('boxOpen')) {
    toggleNoteInput(localStorage.getItem('boxOpen'));
    localStorage.removeItem('boxOpen');
  }
};

const saveNote = function(i) {
  if (addNoteForms[i].reportValidity()) {
    persistOpenedQuestion(i);
    persistOpenedEditBox(i);
    persistScrollLocation();
    addNoteForms[i].submit();
  }
};

const deleteNote = function(i) {
  persistOpenedQuestion(noteDeleteAnswerCounters[i].value);
  persistScrollLocation();
  deleteNoteForms[i].submit();
};

const cancelAddNote = function(i) {
  toggleNoteInput(i);
};

window.addEventListener('DOMContentLoaded', function() {
  retrieveOpenedQuestion();
  getScrollLocation();

  for (let i = 0; i < addNoteButtons.length; i++) {

    i % 2 === 0 ? noteInputs[i].style.backgroundColor = "#ffffff" : noteInputs[i].style.backgroundColor = "#fafafa";

    addNoteButtons[i].addEventListener("click", () => { toggleNoteInput(i); });
    cancelNoteButtons[i].addEventListener("click", () => { cancelAddNote(i); });
    saveNoteButtons[i].addEventListener("click", () => { saveNote(i); });
  }

  for (let i = 0; i < deleteNoteButtons.length; i++) {
    deleteNoteButtons[i].addEventListener("click", () => { deleteNote(i); });
  }
});
