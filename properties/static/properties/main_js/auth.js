document.addEventListener("DOMContentLoaded", function() {
    const authLoginForm = document.getElementById('authLoginForm');
    const authSignupForm = document.getElementById('authSignupForm');
    const authOtpForm = document.getElementById('authOtpForm');
    
    const authModalLabel = document.getElementById('authModalLabelNamespace');

    // Switch to Signup
    document.getElementById('authShowSignup')?.addEventListener('click', e=>{
        e.preventDefault();
        authLoginForm.style.display = 'none';
        authOtpForm.style.display = 'none';
        authSignupForm.style.display = 'block';
       
        authModalLabel.innerText = 'Sign Up';
    });

    // Switch to Login
    document.getElementById('authShowLogin')?.addEventListener('click', e=>{
        e.preventDefault();
        authSignupForm.style.display = 'none';
        authOtpForm.style.display = 'none';
        authLoginForm.style.display = 'block';
     
        authModalLabel.innerText = 'Login';
    });

    // Switch to OTP Login
    document.getElementById('otpLoginBtn')?.addEventListener('click', e=>{
        e.preventDefault();
        authLoginForm.style.display = 'none';
        authSignupForm.style.display = 'none';
        authOtpForm.style.display = 'block';
        
        authModalLabel.innerText = 'Login with OTP';
    });

    // Back to normal login from OTP
    document.getElementById('authShowLoginFromOtp')?.addEventListener('click', e=>{
        e.preventDefault();
        authOtpForm.style.display = 'none';
        authLoginForm.style.display = 'block';
        authModalLabel.innerText = 'Login';
    });

    // Helper for toast notifications
    function showToast(msg) {
        const toastEl = document.getElementById('toastMessage');
        toastEl.querySelector('.toast-body').innerText = msg;
        const toast = new bootstrap.Toast(toastEl);
        toast.show();
    }

    // Send OTP
    document.getElementById('otpSendForm')?.addEventListener('submit', async function(e){
        e.preventDefault();
        const identifier = this.identifier.value;
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        const res = await fetch("/send-login-otp/", {
            method: "POST",
            headers: {"X-CSRFToken": csrfToken, "Content-Type": "application/json"},
            body: JSON.stringify({identifier})
        });

        const data = await res.json();
        if(data.success){
            showToast("OTP sent successfully!");
            this.style.display = 'none';
            document.getElementById('otpVerifyForm').style.display = 'block';
            document.getElementById('otpIdentifier').value = identifier;
        } else {
            showToast(data.error || "Failed to send OTP");
        }
    });

    // Verify OTP
// Verify OTP
document.getElementById('otpVerifyForm')?.addEventListener('submit', async function(e){
    e.preventDefault();
    const identifier = document.getElementById('otpIdentifier').value;
    const otp = this.otp.value;
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    try {
        const res = await fetch("/verify-login-otp/", {
            method: "POST",
            headers: {"X-CSRFToken": csrfToken, "Content-Type": "application/json"},
            body: JSON.stringify({identifier, otp})
        });

        const data = await res.json();

        if(data.success){
            // Show success message
            showToast("✅ Logged in successfully!", "success");

            // Hide OTP form
            this.style.display = 'none';
            document.getElementById('authOtpForm').style.display = 'none';

            // Redirect after short delay
            setTimeout(() => {
                window.location.href = "/index/"; // Change to dashboard if needed
            }, 1200);

        } else {
            showToast(data.error || "❌ Invalid or expired OTP", "error");
        }

    } catch(err) {
        showToast("❌ Error verifying OTP: " + err, "error");
    }
});
   
    // Show Forgot Password form
document.getElementById('authShowForgotPassword')?.addEventListener('click', e => {
    e.preventDefault();
    authLoginForm.style.display = 'none';
    authSignupForm.style.display = 'none';
    authOtpForm.style.display = 'none';
    authForgotPasswordForm.style.display = 'block';
    authModalLabel.innerText = 'Reset Password';
});

// Back to Login from Forgot Password
document.getElementById('authShowLoginFromForgot')?.addEventListener('click', e => {
    e.preventDefault();
    authForgotPasswordForm.style.display = 'none';
    authLoginForm.style.display = 'block';
    authModalLabel.innerText = 'Login';
});




});

const forgotSendForm = document.getElementById('forgotPasswordSendForm');
const forgotVerifyForm = document.getElementById('forgotPasswordVerifyForm');
const resetOtpIdentifier = document.getElementById('resetOtpIdentifier');

forgotSendForm?.addEventListener('submit', async function(e) {
    e.preventDefault();
    const identifier = this.identifier.value;
    const csrfToken = this.querySelector('[name=csrfmiddlewaretoken]').value;

    const res = await fetch("/api/send-password-reset-otp/", {
        method: "POST",
        headers: {"X-CSRFToken": csrfToken, "Content-Type": "application/json"},
        body: JSON.stringify({identifier})
    });

    const data = await res.json();
    if(data.success){
        alert("OTP sent! Check your email.");
        this.style.display='none';
        forgotVerifyForm.style.display='block';
        resetOtpIdentifier.value = identifier;
    } else {
        alert(data.error || "Failed to send OTP");
    }
});

forgotVerifyForm?.addEventListener('submit', async function(e) {
    e.preventDefault();
    const identifier = resetOtpIdentifier.value;
    const otp = this.otp.value;
    const new_password = this.new_password.value;
    const csrfToken = this.querySelector('[name=csrfmiddlewaretoken]').value;

    const res = await fetch("/api/verify-password-reset-otp/", {
        method: "POST",
        headers: {"X-CSRFToken": csrfToken, "Content-Type": "application/json"},
        body: JSON.stringify({identifier, otp, new_password})
    });

    const data = await res.json();
    if(data.success){
        alert("Password reset successful!");
        forgotVerifyForm.style.display='none';
        authForgotPasswordForm.style.display='none';
        authLoginForm.style.display='block';
        authModalLabel.innerText = 'Login';
    } else {
        alert(data.error || "Invalid OTP or password");
    }
});



// js for autocomplete city
document.addEventListener("DOMContentLoaded", function() {
    const postBtn = document.getElementById("postPropertyBtn");
    if (!postBtn) return;

    const isAuthenticated = postBtn.dataset.authenticated === "true";
    const postUrl = postBtn.dataset.postUrl;

    postBtn.addEventListener("click", function(event) {
        event.preventDefault();

        if (isAuthenticated) {
            // Check if user can post (free posts / wallet)
            fetch("/check_post_eligibility/")
                .then(response => response.json())
                .then(data => {
                    if (data.can_post) {
                        window.location.href = postUrl;
                    } else {
                        // Show plan modal
                        const planModalEl = document.getElementById('planModal');
                        if (planModalEl) {
                            new bootstrap.Modal(planModalEl).show();
                        }
                    }
                })
                .catch(err => console.error(err));
        } else {
            // Show login modal
            const loginModalEl = document.getElementById("authModalNamespace");
            if (loginModalEl) {
                new bootstrap.Modal(loginModalEl).show();
            }
        }
    });
});
