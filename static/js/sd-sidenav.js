/* Register sidenav and related variables */
const elems = document.querySelectorAll('.sidenav-fixed'),
      instances = M.Sidenav.init(elems, {}/* options */),
      elem = document.querySelector('.sidenav-fixed'),
      instance = M.Sidenav.getInstance(elem);

/* Is the window above 992 pixels */
const isWindowFullSize = function() {
  return window.innerWidth > 992;
};

/* Change CSS to add padding when sidenav opened */
const addSidenavPadding = function() {
  document.getElementById('base-header').style.paddingLeft = "300";
  document.getElementById('base-main').style.paddingLeft = "300";
};

/* Change CSS to remove padding when sidenav closed */
const removeSidenavPadding = function() {
  document.getElementById('base-header').style.paddingLeft = "0";
  document.getElementById('base-main').style.paddingLeft = "0";
};

/* Adjusts navbar and body main padding if window is > 992px width */
const fixPaddingWidth = function() {
  if (!isWindowFullSize()) {
    removeSidenavPadding();
  } else if (isWindowFullSize() && JSON.parse(localStorage.getItem('sidenavOpen'))) {
    addSidenavPadding();
  }
};

/* Open sidenav */
const openSideNav = function() {
  document.getElementById("slide-out").classList.remove("hide");
  instance.open();
  if (isWindowFullSize()) {
    addSidenavPadding();
  }
};

/* Close sidenav */
const closeSideNav = function() {
  document.getElementById("slide-out").classList.add("hide");
  instance.close();
  if (isWindowFullSize()) {
    removeSidenavPadding();
  }
};

/* Toggle sidebar */
const toggleSidebar = function() {
  instance.isOpen ? closeSideNav() : openSideNav();
  if (isWindowFullSize()) {
    localStorage.setItem('sidenavOpen', JSON.stringify(instance.isOpen));
  }
};

/* Initialize sidenav to close and load storage */
const initSideNav = function() {
  /* Open sidebar if saved state is to open */
  if ((JSON.parse(localStorage.getItem('sidenavOpen')) && isWindowFullSize())
      || (JSON.parse(localStorage.getItem('sidenavOpen')) == null)) {
    instance.isOpen = false;
    toggleSidebar();
    localStorage.setItem('sidenavOpen', JSON.stringify(instance.isOpen));
    /* Otherwise re-initialize to closed  */
  } else {
    instance.isOpen = true;
    toggleSidebar();
    localStorage.setItem('sidenavOpen', JSON.stringify(instance.isOpen));
  }
  /* Check padding and fix depending on sidebar closed/open status */
  fixPaddingWidth();
};

/* Listen for window size changes */
window.addEventListener('resize', function() {
  fixPaddingWidth();
});

/* Listener for page load */
window.addEventListener('DOMContentLoaded', (event) => {
    initSideNav();
});

/* Listen for menu button clicks */
document.querySelector("#toggle_sidenav").addEventListener('click', function() {
  toggleSidebar();
});
