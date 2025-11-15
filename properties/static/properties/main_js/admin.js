// Helper function to get JSON data safely
function getJsonData(id) {
  const el = document.getElementById(id);
  if (!el) return [];
  try {
    return JSON.parse(el.textContent);
  } catch (e) {
    return [];
  }
}

// User Growth Data
const userMonths = getJsonData("user-months");
const userData = getJsonData("user-data");

// Enquiries Data
const enquiryObj = getJsonData("enquiry-data");
const enquiryMonths = enquiryObj.months || [];
const enquiryCounts = enquiryObj.counts || [];

// Chart.js Global Defaults (for clean modern look)
Chart.defaults.font.family = "'Inter', 'Segoe UI', 'Helvetica Neue', sans-serif";
Chart.defaults.font.size = 13;
Chart.defaults.color = "#555";
Chart.defaults.plugins.legend.position = "bottom";
Chart.defaults.plugins.legend.labels.boxWidth = 12;
Chart.defaults.plugins.tooltip.backgroundColor = "rgba(0,0,0,0.7)";
Chart.defaults.plugins.tooltip.titleFont = {weight: "600"};

// User Growth Line Chart
if (document.getElementById("userChart")) {
  new Chart(document.getElementById("userChart"), {
    type: "line",
    data: {
      labels: userMonths,
      datasets: [{
        label: "Users",
        data: userData,
        borderColor: "#0d6efd",
        backgroundColor: "rgba(13, 110, 253, 0.2)",
        tension: 0.4,
        fill: true,
        borderWidth: 2,
        pointRadius: 5,
        pointBackgroundColor: "#0d6efd",
        pointBorderColor: "#fff",
        pointHoverRadius: 7
      }]
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { display: false } },
        y: { grid: { color: "rgba(0,0,0,0.05)" }, ticks: { stepSize: 5 } }
      }
    }
  });
}

// Enquiries Bar Chart
if (document.getElementById("enquiryChart")) {
  new Chart(document.getElementById("enquiryChart"), {
    type: "bar",
    data: {
      labels: enquiryMonths,
      datasets: [{
        label: "Enquiries",
        data: enquiryCounts,
        backgroundColor: "rgba(255, 193, 7, 0.7)",
        borderRadius: 8, // rounded bars
        borderSkipped: false
      }]
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { display: false } },
        y: { grid: { color: "rgba(0,0,0,0.05)" }, ticks: { stepSize: 5 } }
      }
    }
  });
}



  document.addEventListener("DOMContentLoaded", function() {
    const sidebar = document.querySelector(".sidebar");
    const overlay = document.createElement("div");
    overlay.classList.add("sidebar-overlay");
    document.body.appendChild(overlay);

    // Add menu toggle button dynamically if missing
    let toggleBtn = document.querySelector(".menu-toggle");
    if (!toggleBtn) {
      const navbar = document.querySelector(".navbar");
      if (navbar) {
        toggleBtn = document.createElement("button");
        toggleBtn.classList.add("menu-toggle", "me-3");
        toggleBtn.innerHTML = '<i class="fas fa-bars"></i>';
        navbar.prepend(toggleBtn);
      }
    }

    // Toggle sidebar on button click
    toggleBtn.addEventListener("click", () => {
      sidebar.classList.toggle("active");
      overlay.classList.toggle("show");
    });

    // Close sidebar when clicking outside
    overlay.addEventListener("click", () => {
      sidebar.classList.remove("active");
      overlay.classList.remove("show");
    });
  });

