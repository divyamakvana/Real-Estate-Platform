//  login and signup




// --- Search Box Placeholder Rotator ---
const searchcity = document.getElementById("searchInput");
if (searchcity) {
  const placeholders = [
    "Search by City",
    "Search by Location",
    "Search by Landmark",
    "Search by Area"
  ];
  let index = 0;

  setInterval(() => {
    index = (index + 1) % placeholders.length;
    searchcity.setAttribute("placeholder", placeholders[index]);
  }, 1000);
}

// --- Toggle Password Fields ---
const toggleBtn = document.getElementById("togglePasswordFields");
const fields = document.getElementById("passwordFields");
if (toggleBtn && fields) {
  toggleBtn.addEventListener("click", function () {
    fields.style.display =
      (fields.style.display === "none" || fields.style.display === "")
        ? "block"
        : "none";
  });
}

// --- Wishlist Toggle ---

document.addEventListener('DOMContentLoaded', function () {
  const buttons = document.querySelectorAll('.shortlist-btn');

  buttons.forEach(button => {
    button.addEventListener('click', function (e) {
      e.preventDefault();
      const propertyId = this.dataset.propertyId;
      const icon = this.querySelector('i');

      fetch("{% url 'toggle_shortlist' %}", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": "{{ csrf_token }}",
        },
        body: JSON.stringify({ property_id: propertyId }),
      })
        .then(response => response.json())
        .then(data => {
          if (data.status === "added") {
            icon.classList.remove('bi-heart');
            icon.classList.add('bi-heart-fill', 'text-danger');
          } else if (data.status === "removed") {
            icon.classList.remove('bi-heart-fill', 'text-danger');
            icon.classList.add('bi-heart');
          }
        });
    });
  });
});



//================= JS for Accessible Modal Switching ================= -->

// validation

document.addEventListener("DOMContentLoaded", function () {

  const loginForm = document.querySelector("#authLoginForm form");
  const signupForm = document.querySelector("#authSignupForm form");

  // ---------------- Signup Validation ----------------
  const signupFields = ["full_name", "email", "phone", "password1", "password2"];
  signupFields.forEach(fieldName => {
    const input = signupForm?.[fieldName];
    input?.addEventListener("input", function () {
      clearError(input);
      validateSignupField(input);
    });
  });

  // ---------------- Login Validation ----------------
  ["identifier", "password"].forEach(fieldName => {
    const input = loginForm?.[fieldName];
    input?.addEventListener("input", function () {
      clearError(input);
      if (input.value.trim() === "") showError(input, "This field is required");
    });
  });

  // ---------------- Helper Functions ----------------
  function showError(input, message) {
    clearError(input);
    const error = document.createElement("div");
    error.className = "auth-error";
    error.innerText = message;
    input.parentNode.appendChild(error);
  }

  function clearError(input) {
    const prevError = input.parentNode.querySelector(".auth-error");
    if (prevError) prevError.remove();
  }

  function validateSignupField(input) {
    const value = input.value.trim();
    const name = input.name;

    if (name === "full_name" && value === "") showError(input, "Full Name is required");

    if (name === "email") {
      if (value === "") showError(input, "Email is required");
      else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) showError(input, "Invalid email format");
    }

    if (name === "phone") {
      if (value === "") showError(input, "Mobile number is required");
      else if (!/^\d{10}$/.test(value)) showError(input, "Enter a valid 10-digit mobile number");
    }

    if (name === "password1" && value === "") showError(input, "Password is required");

    if (name === "password2") {
      if (value === "") showError(input, "Confirm password is required");
      else if (value !== signupForm.password1.value.trim()) showError(input, "Passwords do not match");
    }
  }

});





// for heart


document.addEventListener("DOMContentLoaded", function () {
  const tabLinks = document.querySelectorAll('[data-bs-toggle="tab"]');

  tabLinks.forEach(tab => {
    tab.addEventListener("shown.bs.tab", function (e) {
      const targetId = e.target.getAttribute("href");
      const targetElement = document.querySelector(targetId);

      if (targetElement) {
        if (targetId === "#overview") {
          window.scrollTo({ top: 0, behavior: "smooth" });
        } else {
          targetElement.scrollIntoView({ behavior: "smooth", block: "start" });
        }
      }
    });
  });
});

var dropdownElementList = [].slice.call(document.querySelectorAll('.dropdown-toggle'))
var dropdownList = dropdownElementList.map(function (dropdownToggleEl) {
  return new bootstrap.Dropdown(dropdownToggleEl)
})











// emi calc page
function openEmiTab(tabId, element) {
  document.getElementById('emiCalculator').style.display = 'none';
  document.getElementById('emiFaq').style.display = 'none';

  const tabs = document.getElementsByClassName('emi-tab');
  for (let i = 0; i < tabs.length; i++) tabs[i].classList.remove('active');

  document.getElementById(tabId).style.display = 'block';
  element.classList.add('active');
}

function calculateEmi() {
  const P = parseFloat(document.getElementById('emiLoanAmount').value);
  const annualRate = parseFloat(document.getElementById('emiInterestRate').value);
  const tenureYears = parseFloat(document.getElementById('emiTenure').value);

  if (!P || !annualRate || !tenureYears) {
    document.getElementById('emiResultDisplay').innerHTML = "Please fill all fields!";
    return;
  }

  const r = annualRate / (12 * 100);
  const n = tenureYears * 12;
  const emi = (P * r * Math.pow(1 + r, n)) / (Math.pow(1 + r, n) - 1);
  const totalPayable = emi * n;

  document.getElementById('emiResultDisplay').innerHTML =
    `Monthly EMI: ₹${emi.toFixed(2)}<br>Total Payable: ₹${totalPayable.toFixed(2)}`;
}

// viwe page shrtlist

window.onload = function () {
  console.log("✅ Window loaded - shortlist handler attached");

  const shortlistBtn = document.querySelector(".short");
  if (shortlistBtn) {
    console.log("🎯 Found shortlist button:", shortlistBtn);

    shortlistBtn.addEventListener("click", function () {
      console.log("🔥 Shortlist button clicked");

      const propertyId = this.getAttribute("data-property-id");
      fetch("/toggle-shortlist/", {
        method: "POST",
        headers: {
          "X-CSRFToken": getCookie("csrftoken"),
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: `property_id=${propertyId}`,
      })
        .then((res) => res.json())
        .then((data) => {
          console.log("Server response:", data);

          if (data.status === "added") {
            this.classList.remove("btn-outline-primary");
            this.classList.add("btn-danger");
            this.innerHTML = "♥ Shortlisted";
          } else if (data.status === "removed") {
            this.classList.remove("btn-danger");
            this.classList.add("btn-outline-primary");
            this.innerHTML = "♡ Shortlist";
          }
        })
        .catch((err) => console.error("Error:", err));
    });
  } else {
    console.log("❌ No shortlist button found");
  }
};

// Helper → CSRF
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}



// explore city

// static/properties/main_js/main.js
document.addEventListener("DOMContentLoaded", function () {

  // --- Helpers & elements
  const cityInput = document.getElementById("city-input");
  const suggestionsBox = document.getElementById("city-suggestions");
  const cityIdInput = document.getElementById("city-id");

  // AbortController so rapid typing cancels previous fetch
  let ac = null;

  if (cityInput && suggestionsBox && cityIdInput) {
    cityInput.addEventListener("input", function () {
      const q = this.value.trim();

      // Reset selected city id whenever user types
      cityIdInput.value = "";

      // Hide if too short
      if (q.length < 2) {
        suggestionsBox.style.display = "none";
        suggestionsBox.innerHTML = "";
        if (ac) { ac.abort(); ac = null; }
        return;
      }

      // Cancel previous request
      if (ac) ac.abort();
      ac = new AbortController();

      fetch(`/city-autocomplete/?q=${encodeURIComponent(q)}`, { signal: ac.signal })
        .then(res => res.json())
        .then(data => {
          suggestionsBox.innerHTML = "";
          if (!Array.isArray(data) || data.length === 0) {
            suggestionsBox.style.display = "none";
            return;
          }
          data.forEach(city => {
            const btn = document.createElement("button");
            btn.type = "button";
            btn.className = "list-group-item list-group-item-action";
            btn.textContent = city.name;
            btn.dataset.id = city.id;
            btn.addEventListener("click", function () {
              cityInput.value = this.textContent;
              cityIdInput.value = this.dataset.id;
              suggestionsBox.style.display = "none";
            });
            suggestionsBox.appendChild(btn);
          });
          suggestionsBox.style.display = "block";
        })
        .catch(err => {
          if (err.name !== "AbortError") console.error("Autocomplete error:", err);
        });
    });

    // Close suggestions when clicking outside
    document.addEventListener("click", function (ev) {
      if (!ev.target.closest("#city-suggestions") && ev.target !== cityInput) {
        suggestionsBox.style.display = "none";
      }
    });
  }

  // --- Prefill modal when clicking a city card on the page
  document.querySelectorAll(".city-card").forEach(card => {
    card.addEventListener("click", function () {
      const id = this.dataset.cityId || this.dataset.city || this.getAttribute('data-city-id');
      const name = this.dataset.cityName || this.dataset.cityName || this.getAttribute('data-city-name') || this.querySelector('h6')?.textContent || "";
      // fill inputs when modal opens
      const modal = document.getElementById("cityModal");
      // If modal exists, fill its inputs
      if (modal) {
        const mi = modal.querySelector("#city-input");
        const hid = modal.querySelector("#city-id");
        if (mi) mi.value = name;
        if (hid) hid.value = id;
        // hide suggestions if visible
        const s = modal.querySelector("#city-suggestions");
        if (s) s.style.display = "none";
      }
    });
  });

});


// city carousal js








// delete property in modal in user manage_properties page
document.addEventListener("DOMContentLoaded", function () {
  let deleteId = null;
  const deleteModalEl = document.getElementById("deleteModal");

  // ⛔ FIX: only initialize modal if it exists
  if (deleteModalEl) {
    const deleteModal = new bootstrap.Modal(deleteModalEl);

    // When clicking delete → open modal
    document.querySelectorAll(".delete-btn").forEach(btn => {
      btn.addEventListener("click", function (e) {
        e.preventDefault();
        deleteId = this.dataset.id;
        deleteModal.show();
      });
    });

    // When confirming delete → send request
    const confirmDeleteBtn = document.getElementById("confirmDelete");
    if (confirmDeleteBtn) {
      confirmDeleteBtn.addEventListener("click", function () {
        if (!deleteId) return;

        const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;

        fetch(`/delete-property/${deleteId}/`, {
          method: "POST",
          headers: {
            "X-CSRFToken": csrfToken,
            "X-Requested-With": "XMLHttpRequest"
          }
        })
          .then(res => res.json())
          .then(data => {
            if (data.success) {
              document.getElementById(`property-${deleteId}`).remove();
            } else {
              alert(data.error || "Failed to delete property.");
            }
            deleteModal.hide();
          })
          .catch(err => console.error("Delete error:", err));
      });
    }
  }
});


// js for update availability like sold rented 
document.addEventListener("DOMContentLoaded", function () {
  const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;

  // === Availability Update ===
  document.querySelectorAll(".update-availability").forEach(btn => {
    btn.addEventListener("click", function (e) {
      e.preventDefault();

      const propertyId = this.dataset.id;
      const status = this.dataset.status;

      fetch(`/update-availability/${propertyId}/${status}/`, {
        method: "POST",
        headers: {
          "X-CSRFToken": csrfToken,
          "X-Requested-With": "XMLHttpRequest",
        },
      })
        .then(res => res.json())
        .then(data => {
          if (data.success) {
            // Update badge text & color
            const badge = document.querySelector(`#property-${propertyId} td span.badge`);
            badge.textContent = status.charAt(0).toUpperCase() + status.slice(1);

            // reset classes
            badge.className = "badge";
            if (status === "available") badge.classList.add("bg-success");
            if (status === "rented") badge.classList.add("bg-warning", "text-dark");
            if (status === "sold") badge.classList.add("bg-danger");
          } else {
            alert(data.error || "Failed to update availability.");
          }
        })
        .catch(err => console.error("Update error:", err));
    });
  });
});

// js for about section
// ABOUT SECTION: continuous multi-phrase typing + zoom + fade, robust (no stacking timers)
document.addEventListener("DOMContentLoaded", function () {
  const section = document.getElementById("aboutSection");
  if (!section) {
    console.warn("aboutSection not found — skipping about animations");
    return;
  }

  const aboutImage = document.getElementById("aboutImage");
  const aboutContent = section.querySelector(".about-content"); // container that fades in
  const aboutHeading = document.getElementById("aboutHeading");
  const aboutText = document.getElementById("aboutText");
  const aboutBtn = section.querySelector(".about-btn");

  // fallback selectors
  if (!aboutHeading) {
    console.error("aboutHeading not found");
    return;
  }

  // phrases to cycle through
  const phrases = [
    "Considering finding your dream home?",
    "We make real estate simple.",
    "Your property, our priority."
  ];

  // Save original (or use data-original)
  const original = aboutHeading.dataset.original || phrases[0];
  aboutHeading.dataset.original = original;

  // Keep track of running typing loop so we can stop it
  let typingController = null;
  let revealTimers = []; // stagger timers

  function clearRevealTimers() {
    revealTimers.forEach(t => clearTimeout(t));
    revealTimers = [];
  }

  function stopTypingController() {
    if (typingController && typeof typingController.stop === "function") {
      typingController.stop();
      typingController = null;
    }
  }

  // create a typing loop controller which we can stop
  // returns { stop: fn }
  function startTypeLoopMulti(el, phrasesArr, typeSpeed = 80, deleteSpeed = 45, pause = 900) {
    let phraseIndex = 0;
    let i = 0;
    let deleting = false;
    let timerId = null;
    let stopped = false;

    function tick() {
      if (stopped) return;
      const current = phrasesArr[phraseIndex];

      if (!deleting) {
        // type forward
        el.textContent = current.slice(0, i);
        i++;
        if (i > current.length) {
          deleting = true;
          timerId = setTimeout(tick, pause);
          return;
        }
        timerId = setTimeout(tick, typeSpeed);
      } else {
        // deleting
        el.textContent = current.slice(0, i);
        i--;
        if (i < 0) {
          deleting = false;
          phraseIndex = (phraseIndex + 1) % phrasesArr.length;
          timerId = setTimeout(tick, pause);
          return;
        }
        timerId = setTimeout(tick, deleteSpeed);
      }
    }

    // start
    tick();

    return {
      stop() {
        stopped = true;
        if (timerId) clearTimeout(timerId);
      }
    };
  }

  // animate in: zoom image, reveal content, start typing loop, reveal paragraph and button
  function animateIn() {
    // Safety: if already running, do nothing (or restart)
    if (typingController) {
      // already running - do not start a second loop
      return;
    }

    // clear any previous state
    clearRevealTimers();
    stopTypingController();
    aboutHeading.classList.remove("typing");
    aboutHeading.textContent = "";

    // image zoom
    if (aboutImage) aboutImage.classList.add("zoomed");

    // show content container (fade up)
    // small delay so zoom feels cinematic
    revealTimers.push(setTimeout(() => aboutContent.classList.add("show"), 60));

    // start typing loop after a slight delay
    revealTimers.push(setTimeout(() => {
      aboutHeading.classList.add("typing");
      typingController = startTypeLoopMulti(aboutHeading, phrases, 80, 45, 900);
    }, 260));

    // reveal paragraph and button with stagger
    revealTimers.push(setTimeout(() => aboutText.classList.add("show"), 900));
    revealTimers.push(setTimeout(() => aboutBtn && aboutBtn.classList.add("show"), 1150));
  }

  // animate out: remove classes and stop typing
  function animateOut() {
    // clear timers
    clearRevealTimers();

    // stop typing loop
    stopTypingController();

    // reset UI
    if (aboutImage) aboutImage.classList.remove("zoomed");
    aboutContent.classList.remove("show");
    aboutText.classList.remove("show");
    if (aboutBtn) aboutBtn.classList.remove("show");
    aboutHeading.classList.remove("typing");
    // clear heading text so next entrance retypes
    aboutHeading.textContent = "";
  }

  // IntersectionObserver to run continuously (each time enters view)
  if ("IntersectionObserver" in window) {
    const obs = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          // start animation
          animateIn();
        } else {
          // reset so it can replay later
          animateOut();
        }
      });
    }, { threshold: 0.35 });
    obs.observe(section);
  } else {
    // fallback: use scroll check
    function onScroll() {
      const rect = section.getBoundingClientRect();
      const visible = rect.top < window.innerHeight * 0.85 && rect.bottom > window.innerHeight * 0.15;
      if (visible) animateIn(); else animateOut();
    }
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  // debug
  console.log("About section animations initialized (continuous typing loop).");
});

// post property page js for city and location


// js for adding a review page

// function setupAutocomplete(inputId, suggestionsId, url, extraParam = null) {
//     const input = document.getElementById(inputId);
//     const suggestions = document.getElementById(suggestionsId);

//     input.addEventListener("keyup", () => {
//         let query = input.value;
//         if (query.length < 2) {
//             suggestions.innerHTML = "";
//             return;
//         }

//         let finalUrl = url + "?q=" + query;
//         if (extraParam) {
//             let cityVal = document.getElementById(extraParam).value;
//             finalUrl += "&city=" + cityVal;
//         }

//         fetch(finalUrl)
//             .then(res => res.json())
//             .then(data => {
//                 suggestions.innerHTML = "";
//                 data.forEach(item => {
//                     let li = document.createElement("li");
//                     li.classList.add("list-group-item");
//                     li.textContent = item;
//                     li.addEventListener("click", () => {
//                         input.value = item;
//                         suggestions.innerHTML = "";
//                     });
//                     suggestions.appendChild(li);
//                 });
//             });
//     });
// }


function setupAutocomplete(inputId, suggestionsId, url, extraParam = null) {
  const input = document.getElementById(inputId);
  const suggestions = document.getElementById(suggestionsId);

  // Only proceed if both elements exist
  if (!input || !suggestions) return;

  input.addEventListener("keyup", () => {
    let query = input.value;
    if (query.length < 2) {
      suggestions.innerHTML = "";
      return;
    }

    let finalUrl = url + "?q=" + encodeURIComponent(query);
    if (extraParam) {
      const extraEl = document.getElementById(extraParam);
      if (extraEl) finalUrl += "&city=" + encodeURIComponent(extraEl.value);
    }

    fetch(finalUrl)
      .then(res => res.json())
      .then(data => {
        suggestions.innerHTML = "";
        data.forEach(item => {
          const li = document.createElement("li");
          li.classList.add("list-group-item");
          li.textContent = item;
          li.addEventListener("click", () => {
            input.value = item;
            suggestions.innerHTML = "";
          });
          suggestions.appendChild(li);
        });
      })
      .catch(err => console.error("Autocomplete fetch error:", err));
  });
}




document.addEventListener("DOMContentLoaded", () => {
  setupAutocomplete("cityInput", "citySuggestions", "/ajax/city-suggestions/");
  setupAutocomplete("localityInput", "localitySuggestions", "/ajax/locality-suggestions/", "cityInput");
});






function switchTab(type, el) {
  // Set active button UI
  document.querySelectorAll('.tabs button').forEach(btn => btn.classList.remove('active'));
  el.classList.add('active');

  // Update hidden deal_type field (backend expects "sale" or "rent")
  const dealField = document.getElementById('dealTypeField');
  dealField.value = type === 'sale' ? 'sale' : type === 'rent' ? 'rent' : 'commercial';

  // Show/Hide relevant fields
  const bhk = document.getElementById('bhkSelect');
  const commPurpose = document.getElementById('commercialPurposeSelect');
  const propType = document.getElementById('propertyTypeSelect');

  if (type === 'commercial') {
    // Show commercial options only
    bhk.classList.add('hidden');
    commPurpose.classList.remove('hidden');

    propType.innerHTML = `
            <option value="office">Office</option>
            <option value="shop">Shop</option>
            <option value="warehouse">Warehouse</option>
        `;
  } else {
    // Buy or Rent → use same property types
    bhk.classList.remove('hidden');
    commPurpose.classList.add('hidden');

    propType.innerHTML = `
            <option value="">Property Type</option>
            <option value="flat">Flat</option>
            <option value="house">House</option>
            <option value="land">Land</option>
            <option value="apartment">Apartment</option>
            <option value="villa">Villa</option>
        `;
  }
}


// // search page js for slider
// document.addEventListener('DOMContentLoaded', () => {
//   const form = document.getElementById('new-filtersForm');
//   const resultsContainer = document.getElementById('new-resultsContainer');
//   const minSlider = document.getElementById('new-minPriceSlider');
//   const maxSlider = document.getElementById('new-maxPriceSlider');
//   const minDisplay = document.getElementById('new-minPriceDisplay');
//   const maxDisplay = document.getElementById('new-maxPriceDisplay');

//   // ✅ Safe functions — check elements exist before using
//   function updateDisplay() {
//     if (minSlider && minDisplay) {
//       minDisplay.textContent = parseInt(minSlider.value || 0).toLocaleString();
//     }
//     if (maxSlider && maxDisplay) {
//       maxDisplay.textContent = parseInt(maxSlider.value || 0).toLocaleString();
//     }
//   }

//   function ensureValidRange() {
//     if (minSlider && maxSlider && parseInt(minSlider.value) > parseInt(maxSlider.value)) {
//       maxSlider.value = minSlider.value;
//     }
//   }

//   // ✅ AJAX filtering (safe)
//   function ajaxFilter() {
//     if (!form || !resultsContainer) return;
//     const formData = new FormData(form);
//     const params = new URLSearchParams(formData).toString();

//     fetch(form.action + '?' + params, {
//       headers: { 'X-Requested-With': 'XMLHttpRequest' }
//     })
//     .then(resp => resp.text())
//     .then(html => resultsContainer.innerHTML = html)
//     .catch(err => console.error('AJAX Filter Error:', err));
//   }

//   // ✅ Add listeners only if elements exist
//   if (form) form.addEventListener('change', ajaxFilter);
//   if (minSlider) {
//     minSlider.addEventListener('input', () => { ensureValidRange(); updateDisplay(); });
//     minSlider.addEventListener('change', ajaxFilter);
//   }
//   if (maxSlider) {
//     maxSlider.addEventListener('input', () => { ensureValidRange(); updateDisplay(); });
//     maxSlider.addEventListener('change', ajaxFilter);
//   }

//   // ✅ Initialize display if sliders exist
//   updateDisplay();
// });

  // message js
  document.addEventListener("DOMContentLoaded", () => {
    var toastElList = [].slice.call(document.querySelectorAll('.toast'))
    toastElList.map(function (toastEl) {
      return new bootstrap.Toast(toastEl).show()
    })
  });









  // js for change pass
  $('#changePasswordForm').on('submit', function (e) {
    e.preventDefault();
    $('#formErrors').html('');
    $('#modalMessage').html('');

    var url = $(this).data('url');  // Get URL from data-url
    var csrf = $(this).find('input[name="csrfmiddlewaretoken"]').val();

    $.ajax({
      url: url,
      type: "POST",
      headers: { "X-CSRFToken": csrf },
      data: $(this).serialize(),
      success: function (data) {
        if (data.success) {
          $('#modalMessage').html(data.message);
          $('#changePasswordForm')[0].reset();
        } else if (data.errors) {
          let errors = '';
          for (const field in data.errors) {
            errors += data.errors[field].join('<br>') + '<br>';
          }
          $('#formErrors').html(errors);
        }
      },
      error: function (xhr) {
        $('#formErrors').html('An error occurred: ' + xhr.status + ' ' + xhr.statusText);
      }
    });
  });


  // js for contact owner
  document.addEventListener("DOMContentLoaded", function () {
    const contactOwnerModal = document.getElementById('contactOwnerModal');
    const contactOwnerForm = document.getElementById('contactOwnerForm');
    const formErrors = document.getElementById('formErrors');
    let contactUrl = "";

    // When modal opens
    contactOwnerModal.addEventListener('show.bs.modal', function (event) {
      const button = event.relatedTarget;
      const propertyId = button.getAttribute('data-property-id');
      contactUrl = button.getAttribute('data-contact-url');  // get URL from button

      contactOwnerForm.querySelector('#property_id').value = propertyId;
      formErrors.innerHTML = '';
      contactOwnerForm.reset();
      contactOwnerForm.querySelector("button[type='submit']").disabled = false;
      contactOwnerForm.querySelector("button[type='submit']").innerText = "Send Message";
    });

    // Handle form submission
    contactOwnerForm.addEventListener('submit', function (e) {
      e.preventDefault();
      formErrors.innerHTML = '';

      const formData = new FormData(contactOwnerForm);

      fetch(contactUrl, {
        method: "POST",
        headers: {
          "X-CSRFToken": formData.get('csrfmiddlewaretoken'),
        },
        body: formData
      })
        .then(response => response.json())
        .then(data => {
          const submitBtn = contactOwnerForm.querySelector("button[type='submit']");
          if (data.status === "success") {
            formErrors.innerHTML = `<div class="alert alert-success">${data.message}</div>`;
            submitBtn.disabled = true;
            submitBtn.innerText = "Already Contacted";
          } else if (data.status === "exists") {
            formErrors.innerHTML = `<div class="alert alert-warning">${data.message}</div>`;
            submitBtn.disabled = true;
            submitBtn.innerText = "Already Contacted";
          } else {
            formErrors.innerHTML = data.errors.map(err => `<div class="text-danger">${err}</div>`).join('');
          }
        })
        .catch(err => {
          console.error("AJAX error:", err);
          formErrors.innerHTML = `<div class="text-danger">An error occurred. Check console for details.</div>`;
        });
    });
  });




  // explore city modal js
  document.addEventListener("DOMContentLoaded", function () {
    const modalCityName = document.getElementById('modalCityName');
    const modalCityInput = document.getElementById('modalCityInput');
    const modalDealType = document.getElementById('modalDealType');

    const modalBhkSelect = document.getElementById('modalBhkSelect');
    const modalCommercialSelect = document.getElementById('modalCommercialPurposeSelect');
    const modalPropertyTypeSelect = document.getElementById('modalPropertyTypeSelect');

    const propertyTypes = {
      sale: ['Flat', 'House', 'Land'],
      rent: ['Flat', 'House'],
      commercial: ['Office', 'Shop', 'Warehouse']
    };

    // Open modal with selected city
    document.querySelectorAll('.city-card').forEach(card => {
      card.addEventListener('click', function () {
        const cityName = this.getAttribute('data-city-name');
        modalCityName.textContent = cityName;
        modalCityInput.value = cityName;

        // default to sale tab
        switchModalTab('sale', document.querySelector('.tabs button[data-type="sale"]'));
      });
    });

    // Tab switch function
    window.switchModalTab = function (type, btn) {
      // Update deal type hidden field
      modalDealType.value = type;

      // Update active button
      btn.closest('.tabs').querySelectorAll('button').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      // Show/hide selects
      if (type === 'commercial') {
        modalBhkSelect.classList.add('hidden');
        modalCommercialSelect.classList.remove('hidden');
      } else {
        modalBhkSelect.classList.remove('hidden');
        modalCommercialSelect.classList.add('hidden');
      }

      // Populate property types
      modalPropertyTypeSelect.innerHTML = '<option value="">Property Type</option>';
      propertyTypes[type].forEach(pt => {
        const opt = document.createElement('option');
        opt.value = pt.toLowerCase();
        opt.textContent = pt;
        modalPropertyTypeSelect.appendChild(opt);
      });
    };
  });



  // js for shoerlist icon at search result page
  // js for service modal
  document.querySelectorAll('.service-trigger').forEach(item => {
    item.addEventListener('click', function () {
      const title = this.getAttribute('data-title');
      const dealType = this.getAttribute('data-deal');

      // update modal title
      document.getElementById('serviceModalLabel').innerText = title;

      // update hidden input
      document.getElementById('dealTypeInput').value = dealType;
    });
  });



// //  for slider
// function ajaxFilter() {
//     const form = document.getElementById('new-filtersForm');
//     const resultsContainer = document.getElementById('new-resultsContainer');
//     const formData = new FormData(form);
//     const params = new URLSearchParams(formData).toString();

//     fetch(form.action + '?' + params, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
//         .then(resp => resp.text())
//         .then(html => resultsContainer.innerHTML = html);
// }

  
// js for city suggestion at home page

document.addEventListener("DOMContentLoaded", function () {
  const input = document.getElementById("searchInput");
  const suggestionsList = document.getElementById("citySuggestions");

  input.addEventListener("input", function () {
    const query = this.value.trim();
    suggestionsList.innerHTML = "";

    if (query.length === 0) {
      suggestionsList.style.display = "none";
      return;
    }

    fetch(`/ajax/city-suggestions/?q=${query}`)
      .then(response => response.json())
      .then(data => {
        const results = data.results;
        if (results.length === 0) {
          suggestionsList.style.display = "none";
          return;
        }

        results.forEach(city => {
          const li = document.createElement("li");
          li.classList.add("list-group-item", "list-group-item-action");
          li.textContent = city;
          li.addEventListener("click", function () {
            input.value = this.textContent;
            suggestionsList.style.display = "none";
          });
          suggestionsList.appendChild(li);
        });

        suggestionsList.style.display = "block";
      });
  });

  document.addEventListener("click", function (e) {
    if (!input.contains(e.target) && !suggestionsList.contains(e.target)) {
      suggestionsList.style.display = "none";
    }
  });
});

// locality and city suggestions both in service modal

document.addEventListener("DOMContentLoaded", function () {

  function initAutocomplete(inputId, suggestionId) {
    const input = document.getElementById(inputId);
    const suggestionsList = document.getElementById(suggestionId);

    function showSuggestions(data) {
      suggestionsList.innerHTML = "";
      if (!data.length) {
        suggestionsList.style.display = "none";
        return;
      }

      data.forEach(item => {
        const li = document.createElement("li");
        li.classList.add("list-group-item", "list-group-item-action");
        li.textContent = item;
        li.addEventListener("click", function () {
          input.value = item;
          suggestionsList.style.display = "none";
        });
        suggestionsList.appendChild(li);
      });

      suggestionsList.style.display = "block";
    }

    input.addEventListener("input", function () {
      const query = input.value.trim();
      if (!query) return suggestionsList.style.display = "none";

      fetch(`/ajax/location-suggestions/?q=${query}`)
        .then(res => res.json())
        .then(data => showSuggestions(data.results));
    });

    // Hide suggestions if clicking outside
    document.addEventListener("click", function (e) {
      if (!input.contains(e.target) && !suggestionsList.contains(e.target)) {
        suggestionsList.style.display = "none";
      }
    });
  }

  // Initialize autocomplete for both inputs
  initAutocomplete("searchInput", "citySuggestions");
  initAutocomplete("locationInput", "locationSuggestions");

});


// js for search page sidebare filter
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('filtersForm');
    const resultsContainer = document.getElementById('resultsContainer');
    const minSlider = document.getElementById('minPriceSlider');
    const maxSlider = document.getElementById('maxPriceSlider');
    const minDisplay = document.getElementById('minPriceDisplay');
    const maxDisplay = document.getElementById('maxPriceDisplay');

    // ---------------- Price Slider Helpers ----------------
    function updatePriceDisplay() {
        if (minSlider && minDisplay) minDisplay.textContent = parseInt(minSlider.value).toLocaleString();
        if (maxSlider && maxDisplay) maxDisplay.textContent = parseInt(maxSlider.value).toLocaleString();
    }

    function ensureValidRange() {
        if (minSlider && maxSlider && parseInt(minSlider.value) > parseInt(maxSlider.value)) {
            maxSlider.value = minSlider.value;
            updatePriceDisplay();
        }
    }

    // ---------------- AJAX Filter Function ----------------
    function ajaxFilter() {
        if (!form || !resultsContainer) return;

        const formData = new FormData(form);

        // Ensure min/max price is sent
        if (minSlider) formData.set('min_price', minSlider.value);
        if (maxSlider) formData.set('max_price', maxSlider.value);

        const params = new URLSearchParams(formData).toString();

        fetch(`${form.action}?${params}`, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(res => res.text())
        .then(html => {
            resultsContainer.innerHTML = html;

            // Reattach shortlist & call buttons if needed
            attachShortlistButtons();
            attachCallButtons();
        })
        .catch(err => console.error('AJAX filter error:', err));
    }

    // ---------------- Attach Event Listeners ----------------
    if (form) {
        // All inputs except price sliders
        form.querySelectorAll('input[type="radio"], input[type="text"], select').forEach(el => {
            el.addEventListener('change', ajaxFilter);
        });
    }

    if (minSlider) {
        minSlider.addEventListener('input', () => { ensureValidRange(); updatePriceDisplay(); });
        minSlider.addEventListener('change', ajaxFilter);
    }
    if (maxSlider) {
        maxSlider.addEventListener('input', () => { ensureValidRange(); updatePriceDisplay(); });
        maxSlider.addEventListener('change', ajaxFilter);
    }

    // ---------------- Initialize ----------------
    updatePriceDisplay();
});
