/* Initializes modal pop-ups for deleting positions and uploading applicants */
const modalElements = document.querySelectorAll(".modal");
const modalInstances = M.Modal.init(modalElements, {} /* options */ );
const uploadApplicantModal = modalInstances[1];
const uploadModal = modalInstances[2];

const responseModals = document.querySelectorAll(".modal.response-modal") ?  document.querySelectorAll(".modal.response-modal") : null;
const responseModalInstances = document.querySelectorAll(".modal.response-modal") ? M.Modal.init(responseModals, {} /* options */ ) : null;
