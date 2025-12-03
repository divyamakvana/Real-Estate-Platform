// emi.js

// EMI Calculation function - global
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

// Tab Switching

function scrollToSection(sectionId) {
    const element = document.getElementById(sectionId);
    if(element) {
        element.scrollIntoView({behavior: 'smooth', block: 'start'});
    }
}

// faq button js
function toggleFaq(button) {
    const answer = button.nextElementSibling;

    // Toggle active class
    button.classList.toggle('active');

    // Expand or collapse
    if (answer.style.maxHeight) {
        answer.style.maxHeight = null;
        answer.style.padding = "0 20px";
    } else {
        answer.style.maxHeight = answer.scrollHeight + "px";
        answer.style.padding = "10px 20px";
    }
}

function calculateBudget() {
    let income = parseFloat(document.getElementById('monthlyIncome').value);
    let customEmiInput = document.getElementById('customEmi').value;
    let R = parseFloat(document.getElementById('budgetRate').value) / 12 / 100;
    let N = parseFloat(document.getElementById('budgetTenure').value) * 12;

    let emi = customEmiInput ? parseFloat(customEmiInput) : income * 0.4;

    let loanAmount = emi * ((Math.pow(1 + R, N) - 1) / (R * Math.pow(1 + R, N)));
    let totalPayment = emi * N;
    let totalInterest = totalPayment - loanAmount;

    document.getElementById('budgetResult').innerHTML = `
        <strong>Affordable EMI:</strong> ₹${emi.toFixed(2)}<br>
        <strong>Estimated Loan Eligibility:</strong> ₹${loanAmount.toFixed(2)}<br>
        <strong>Total Payable:</strong> ₹${totalPayment.toFixed(2)}<br>
        <strong>Total Interest:</strong> ₹${totalInterest.toFixed(2)}
    `;
}



// loan eligibility
function calculateEMI(principal, annualRate, tenureYears) {
  const r = annualRate / 12 / 100;
  const n = tenureYears * 12;
  return (principal * r * Math.pow(1 + r, n)) / (Math.pow(1 + r, n) - 1);
}

function calculateBorrowableAmount() {
  const age = parseInt(document.getElementById("age").value);
  const occupation = document.getElementById("occupation").value;
  const income = parseFloat(document.getElementById("income").value);
  const existingEmi = parseFloat(document.getElementById("existingEmi").value);
  const tenure = parseInt(document.getElementById("tenure").value);
  const interestRate = parseFloat(document.getElementById("interestRate").value);

  const resultDiv = document.getElementById("loanResult");

  if (
    isNaN(age) || isNaN(income) || isNaN(existingEmi) ||
    isNaN(tenure) || isNaN(interestRate)
  ) {
    resultDiv.innerHTML = "❗ Please fill in all fields correctly.";
    return;
  }

  if (age < 21 || age > 65) {
    resultDiv.innerHTML = "❌ Age must be between 21 and 65.";
    return;
  }

  // FOIR (Fixed Obligations to Income Ratio)
  const maxFOIR = 0.5; // 50% of income
  const availableEMI = income * maxFOIR - existingEmi;

  if (availableEMI <= 0) {
    resultDiv.innerHTML = "❌ You may not be eligible for a loan with current EMIs.";
    return;
  }

  // Reverse calculate max loan based on available EMI
  // Using binary search to find max principal for EMI
  let low = 0, high = 1e8, maxLoan = 0;

  for (let i = 0; i < 30; i++) {
    const mid = (low + high) / 2;
    const emi = calculateEMI(mid, interestRate, tenure);
    if (emi <= availableEMI) {
      maxLoan = mid;
      low = mid;
    } else {
      high = mid;
    }
  }

  const finalEMI = calculateEMI(maxLoan, interestRate, tenure);

  resultDiv.innerHTML = `
    ✅ Based on your inputs, you can borrow up to <strong>₹${Math.round(maxLoan).toLocaleString()}</strong>.<br>
    💸 Estimated EMI: <strong>₹${finalEMI.toFixed(0)}</strong>/month for ${tenure} years at ${interestRate}% interest.
  `;
}


function convertArea() {
    const value = parseFloat(document.getElementById("areaValue").value);
    const fromUnit = document.getElementById("fromUnit").value;
    const toUnit = document.getElementById("toUnit").value;
    const resultDiv = document.getElementById("areaResultDisplay");

    if (!value) {
        resultDiv.innerHTML = " Please enter a value!";
        return;
    }

    // Conversion rates (to sqft as base unit)
    const toSqft = {
        sqft: 1,
        sqm: 10.764,
        sqyd: 9,
        acre: 43560,
        hectare: 107639
    };

    // Convert input value to sqft
    const sqftValue = value * toSqft[fromUnit];

    // Convert sqft to target unit
    const convertedValue = sqftValue / toSqft[toUnit];

    // Show result
    resultDiv.innerHTML = `
         ${value} ${fromUnit.toUpperCase()} = <b>${convertedValue.toFixed(2)}</b> ${toUnit.toUpperCase()}
    `;
}





