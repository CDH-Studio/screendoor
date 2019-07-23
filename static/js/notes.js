const addNoteButtons = document.getElementsByClassName("add-note");

const cancelNoteButtons = document.getElementsByClassName("cancel-note");
const saveNoteButtons = document.getElementsByClassName("save-note");
const addNoteForms = document.getElementsByClassName("note-form");

const deleteNoteForms = document.getElementsByClassName("delete-note-form");
const deleteNoteButtons = document.getElementsByClassName("delete-note");
const noteDeleteAnswerCounters = document.getElementsByClassName("note-delete-answer-counter");

const noteRows = document.getElementsByClassName("notes-row");
const noteAreas = document.getElementsByClassName("notes-area");

const noteTextArea = document.getElementById('note-textarea');

const persistOpenedQuestion = function(i) {
  localStorage.setItem('questionIndex', i);
};

const persistOpenedEditBox = function(i) {
  localStorage.setItem('boxOpen', i);
};

const toggleNoteInput = function(i) {
  if (noteAreas[i].contains(noteTextArea)) {
    noteAreas[i].removeChild(noteTextArea);
    noteTextArea.style.visibility = "hidden";
  } else {
    noteAreas[i].insertBefore(noteTextArea, deleteNoteForms[i].nextSibling);
    noteTextArea.style.visibility = "visible";
  }
};

const retrieveOpenedQuestion = function() {
  if (localStorage.getItem('questionIndex')) {
    questionHeaders[localStorage.getItem('questionIndex')].click();
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
  hideElements(noteInputs[i]);
};

window.addEventListener('DOMContentLoaded', function() {
  retrieveOpenedQuestion();
  getScrollLocation();
  for (let i = 0; i < addNoteButtons.length; i++) {
    addNoteButtons[i].addEventListener("click", () => { toggleNoteInput(i); });
    cancelNoteButtons[i].addEventListener("click", () => { cancelAddNote(i); });
    saveNoteButtons[i].addEventListener("click", () => { saveNote(i); });
  }
  for (let i = 0; i < deleteNoteButtons.length; i++) {
    deleteNoteButtons[i].addEventListener("click", () => { deleteNote(i); });
  }
});
