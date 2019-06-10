/* Clears all local storage except sidebar open boolean */
function clearExceptSidebar() {
  let tempSidebarStatus = JSON.parse(localStorage.getItem('sidenavOpen'));
  localStorage.clear();
  localStorage.setItem('sidenavOpen', tempSidebarStatus);
}
/* Display persisted form information, or if none exists, hide PDF and URL forms */
window.onload = function() {
  if (localStorage.getItem('pdfRequired') === null) {
    document.getElementById('pdf_upload_form').style.display = 'none';
    document.getElementById('url_upload_form').style.display = 'none';
    document.getElementById('position_submit_button').style.display = 'none';
    document.getElementById('radio_pdf').checked = false;
    document.getElementById('radio_url').checked = false;
  } else {
    document.getElementById('pdf_input').required = localStorage.getItem('pdfRequired');
    document.getElementById('url_input').required = !localStorage.getItem('pdfRequired');
    document.getElementById('pdf_path_input').value = localStorage.getItem('pdfText');
    document.getElementById('pdf_input').value = null;
    document.getElementById('url_input').value = localStorage.getItem('urlText');
    document.getElementById('pdf_upload_form').style.display = localStorage.getItem('pdfDisplay');
    document.getElementById('url_upload_form').style.display = localStorage.getItem('urlDisplay');
    document.getElementById('radio_pdf').checked = localStorage.getItem('pdfChecked');
    document.getElementById('radio_url').checked = !localStorage.getItem('pdfChecked');
    clearExceptSidebar();
  }
};
/* Persist the form data to display alongside processed position */
function persistUploaded() {
  localStorage.setItem('pdfRequired', document.getElementById('pdf_input').required);
  localStorage.setItem('pdfText', document.getElementById('pdf_path_input').value);
  localStorage.setItem('urlText', document.getElementById('url_input').value);
  localStorage.setItem('pdfDisplay', document.getElementById('pdf_upload_form').style.display);
  localStorage.setItem('urlDisplay', document.getElementById('url_upload_form').style.display);
  localStorage.setItem('pdfChecked', document.getElementById('radio_pdf').checked);
  localStorage.setItem('urlChecked', document.getElementById('radio_url').checked);
}
/* Show PDF form, hide and clear URL input form */
function showPdf() {
  document.getElementById('pdf_upload_form').style.display = 'block';
  document.getElementById('pdf_input').required = true;
  document.getElementById('url_upload_form').style.display = 'none';
  document.getElementById('url_input').required = false;
  document.getElementById('url_input').value = null;
  document.getElementById('position_submit_button').style.display = 'block';
  document.getElementById('position_submit_button').className = 'right btn';
  document.getElementById('position_submit_button').value = 'Submit';
}
/* Show URL form, hide and clear PDF input form */
function showUrl() {
  document.getElementById('pdf_upload_form').style.display = 'none';
  document.getElementById('pdf_input').required = false;
  document.getElementById('pdf_input').value = null;
  document.getElementById('pdf_path_input').value = null;
  document.getElementById('url_upload_form').style.display = 'block';
  document.getElementById('url_input').required = true;
  document.getElementById('position_submit_button').style.display = 'block';
  document.getElementById('position_submit_button').className = 'right btn disabled';
  document.getElementById('position_submit_button').value = 'Coming soon';
}
