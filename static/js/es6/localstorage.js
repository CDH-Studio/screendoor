/* Clears local storage except the current sidebar status */
const clearExceptSidebar = function() {
  let tempSidebarStatus = JSON.parse(localStorage.getItem("sidenavOpen"));
  localStorage.clear();
  localStorage.setItem("sidenavOpen", tempSidebarStatus);
};

/* Display persisted form information, or if none exists, hide PDF and URL forms */
const initializePositionImportVariables = function() {
  if (localStorage.getItem("pdfRequired") === null) {
    document.getElementById("pdf_upload_form").classList.add("hide");
    document.getElementById("url_upload_form").classList.add("hide");
    document.getElementById("position_submit_button").classList.add("hide");
    document.getElementById("radio_pdf").checked = false;
    document.getElementById("radio_url").checked = false;
  } else {
    document.getElementById("pdf_input").required = localStorage.getItem("pdfRequired") == "true" ? true : false;
    document.getElementById("url_input").required = localStorage.getItem("urlRequired") == "true" ? true : false;
    document.getElementById("pdf_path_input").value = localStorage.getItem("pdfText");
    document.getElementById("pdf_input").value = null;
    document.getElementById("url_input").value = localStorage.getItem("urlText");
    document.getElementById("pdf_upload_form").className = localStorage.getItem("pdfDisplay");
    document.getElementById("url_upload_form").className = localStorage.getItem("urlDisplay");
    document.getElementById("radio_url").checked = localStorage.getItem("urlChecked") == "true" ? true : false;
    document.getElementById("radio_pdf").checked = localStorage.getItem("pdfChecked") == "true" ? true : false;
    document.getElementById("position_submit_button").classList.remove("hide");
    clearExceptSidebar();
  }
};

/* Persist uploaded file names to display alongside applicant processing bar */
const persistPdfNames = function() {
  localStorage.setItem("applicationFiles", document.getElementById("pdf_path_input").value);
};

const persistScrollLocation = function() {
  localStorage.setItem("scroll", window.scrollY);
};

const getScrollLocation = function() {
  if (localStorage.getItem("scroll")) {
    window.scroll(0, localStorage.getItem("scroll"));
    localStorage.removeItem("scroll");
  }
};

/* Persist the form data to display alongside processed position */
const persistUploadForm = function() {
  localStorage.setItem("pdfRequired", document.getElementById("pdf_input").required);
  localStorage.setItem("urlRequired", document.getElementById("url_input").required);
  localStorage.setItem("pdfText", document.getElementById("pdf_path_input").value);
  localStorage.setItem("urlText", document.getElementById("url_input").value);
  localStorage.setItem("pdfDisplay", document.getElementById("pdf_upload_form").classList);
  localStorage.setItem("urlDisplay", document.getElementById("url_upload_form").classList);
  localStorage.setItem("pdfChecked", document.getElementById("radio_pdf").checked);
  localStorage.setItem("urlChecked", document.getElementById("radio_url").checked);
};

/* Show URL form, hide and clear PDF input form */
const showUrl = function() {
  document.getElementById("pdf_upload_form").classList.add("hide");
  document.getElementById("pdf_input").required = false;
  document.getElementById("pdf_input").value = null;
  document.getElementById("pdf_path_input").value = null;
  document.getElementById("url_upload_form").classList.remove("hide");
  document.getElementById("url_input").required = true;
  document.getElementById("position_submit_button").classList.remove("hide");
  document.getElementById("position_submit_button").classList.add("right", "btn");
  document.getElementById("position_submit_button").value = "Submit";
};

/* Show PDF form, hide and clear URL input form */
const showPdf = function() {
  document.getElementById("pdf_upload_form").classList.remove("hide");
  document.getElementById("pdf_input").required = true;
  document.getElementById("url_upload_form").classList.add("hide");
  document.getElementById("url_input").required = false;
  document.getElementById("url_input").value = null;
  document.getElementById("position_submit_button").classList.remove("hide", "disabled");
  document.getElementById("position_submit_button").classList.add("right", "btn");
  document.getElementById("position_submit_button").value = "Submit";
};

/* Displays loading bar for position upload */
const displayLoadingBar = function() {
  document.getElementById("loading-bar").classList.remove("hide");
};

/* Initialize listeners for local storage requirements depending on current page */
const initializeListeners = function() {
  if (window.location.pathname.includes("/position/")) {
    if (document.getElementsByClassName("applicant-sort")) {
      const sortLinks = document.getElementsByClassName("applicant-sort");
      for (let i = 0; i < sortLinks.length; i++) {
        sortLinks[i].addEventListener("click", persistScrollLocation);
      }
      getScrollLocation();
    }
  }

  if (window.location.pathname.includes("/position") || window.location.pathname.includes("/positions")) {
    document.getElementById("upload-applications-form").addEventListener("submit", persistPdfNames);
  } else if (window.location.pathname.includes("/createnewposition")) {
    initializePositionImportVariables();

    document.getElementById("radio_pdf").addEventListener("click", showPdf);
    document.getElementById("radio_url").addEventListener("click", showUrl);
    document.getElementById("position_submit_button").addEventListener("click", function() {
      if (document.getElementById("upload-position").checkValidity()) {
        displayLoadingBar();
        persistUploadForm();
        document.getElementById("upload-position").submit();
      }
    });
    if (document.getElementById("save-button")) {
      document.getElementById("save-button").addEventListener("clock", displayLoadingBar);
    }
    document.getElementById("loading-bar").classList.add("hide");
  }
};

/* Checks for current page and initializes listeners */
window.addEventListener("DOMContentLoaded", function () {
  initializeListeners();
});
