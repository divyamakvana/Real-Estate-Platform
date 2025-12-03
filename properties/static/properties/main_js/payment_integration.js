document.addEventListener("DOMContentLoaded", function () {
    let selectedPropertyId = null;

    // When Contact Owner button is clicked
    document.querySelectorAll(".contact-owner-btn").forEach((btn) => {
        btn.addEventListener("click", function () {
            selectedPropertyId = this.dataset.propertyId;
        });
    });

    // Handle Buy Now buttons inside modal
    document.querySelectorAll(".buy-plan-btn").forEach((planBtn) => {
        planBtn.addEventListener("click", function () {
            const planId = this.dataset.planId;

            if (!selectedPropertyId) {
                alert("Something went wrong. Please try again.");
                return;
            }

            // Initiate payment
            fetch(`/payments/initiate-payment/${planId}/${selectedPropertyId}/`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCookie("csrftoken"),
                    "Accept": "application/json"
                }
            })
                .then((r) => r.json())
                .then((data) => {
                    if (data.redirect) {
                        window.location.href = data.redirect; // Redirect to Paytm
                    } else {
                        alert("Something went wrong, please try again.");
                    }
                })
                .catch((err) => {
                    console.error(err);
                    alert("Payment initiation failed.");
                });
        });
    });

    // Helper function to get CSRF token
    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(";").shift();
    }
});
