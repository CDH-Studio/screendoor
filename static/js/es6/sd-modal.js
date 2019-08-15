/* All modal divs on a page */
const modalElements = document.querySelectorAll(".modal");

/* Array of the modal instances */
const modalInstances = M.Modal.init(modalElements, {} /* options */ );

/* Upload applicant modal */
const uploadApplicantModal = modalInstances[1];

/* Applicants processing modal  */
const uploadModal = modalInstances[2];

const responseModals = document.querySelectorAll(".modal.response-modal") ?  document.querySelectorAll(".modal.response-modal") : null;
const responseModalInstances = document.querySelectorAll(".modal.response-modal") ? M.Modal.init(responseModals, {} /* options */ ) : null;
