// Show/hide fields based on property type
document.addEventListener("DOMContentLoaded", function () {
  const propertyType = document.getElementById("propertyType");

  function toggleFields() {
    const type = propertyType.value;
    document.querySelectorAll(".flat-house, .land, .commercial").forEach(el => el.classList.add("hidden"));
    if (type === "flat" || type === "house") {
      document.querySelectorAll(".flat-house").forEach(el => el.classList.remove("hidden"));
    } else if (type === "land") {
      document.querySelectorAll(".land").forEach(el => el.classList.remove("hidden"));
    } else if (type === "commercial") {
      document.querySelectorAll(".commercial").forEach(el => el.classList.remove("hidden"));
    }
  }
  propertyType.addEventListener("change", toggleFields);
});


// Tabs next/prev
document.addEventListener("DOMContentLoaded", function () {
  const nextButtons = document.querySelectorAll(".next-tab");
  const prevButtons = document.querySelectorAll(".prev-tab");

  function switchTab(tabId) {
    const navLink = document.querySelector(`.nav-link[data-bs-target="#${tabId}"]`);
    if (navLink) new bootstrap.Tab(navLink).show();
  }

  nextButtons.forEach(btn => {
    btn.addEventListener("click", function () {
      const currentTab = document.querySelector(".tab-pane.active");
      let nextTab = currentTab.nextElementSibling;
      while (nextTab && !nextTab.classList.contains("tab-pane")) nextTab = nextTab.nextElementSibling;
      if (nextTab) switchTab(nextTab.getAttribute("id"));
    });
  });

  prevButtons.forEach(btn => {
    btn.addEventListener("click", function () {
      const currentTab = document.querySelector(".tab-pane.active");
      let prevTab = currentTab.previousElementSibling;
      while (prevTab && !prevTab.classList.contains("tab-pane")) prevTab = prevTab.previousElementSibling;
      if (prevTab) switchTab(prevTab.getAttribute("id"));
    });
  });
});


  const citySelect = document.getElementById("city");
  const localitySelect = document.getElementById("locality");
  const pincodeInput = document.getElementById("pincode");

  citySelect.addEventListener("change", function () {
    const cityId = this.value;
    localitySelect.innerHTML = '<option value="">Select Locality</option>';
    pincodeInput.value = "";

    if (localitiesData[cityId]) {
      localitiesData[cityId].forEach(loc => {
        const opt = document.createElement("option");
        opt.value = loc.id;
        opt.textContent = loc.name;
        opt.dataset.pincode = loc.pincode;
        localitySelect.appendChild(opt);
      });
    }
  });

  localitySelect.addEventListener("change", function () {
    const selected = this.options[this.selectedIndex];
    pincodeInput.value = selected.dataset.pincode || "";
  });

  
  

  
// Helper function to read CSRF cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.slice(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


// js for price prediction system

