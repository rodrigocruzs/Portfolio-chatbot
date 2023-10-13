let customerData = {
    age: null,
    maritalStatus: "",
    dependents: null,
    employmentStatus: "",
    annualIncome: null,
    incomeSource: "",
    majorExpensesNext5Years: [],
    financialCommitments: "",
    investmentDuration: null,
    investmentKnowledgeRating: null,
    investmentReaction: "",
    capitalPreference: "",
    debtFeeling: "",
    anticipatedChangesNext3_5Years: null,
    reviewFrequency: "",
    investments: [],
    goals: [],
    riskTolerance: "",
    investmentStyle: "",
};

function showScreen(screenId) {
    // Hide all onboarding screens
    const screens = document.querySelectorAll('.onboarding-screen');
    screens.forEach(screen => {
        screen.classList.remove('flex-display');
        screen.classList.add('hidden');
    });

    // Show the desired screen
    const targetScreen = document.getElementById(screenId);
    targetScreen.classList.remove('hidden');
    targetScreen.classList.add('flex-display');
}

function handleRiskTolerance(option) {
    // Deselect all risk tolerance buttons
    const riskButtons = document.querySelectorAll('#investment-style-form .select-button');
    riskButtons.forEach(button => {
        button.setAttribute('data-selected', 'false');
        button.classList.remove('selected');
    });

    // Highlight the selected button
    const selectedButton = document.querySelector(`#investment-style-form .select-button[onclick="handleRiskTolerance('${option}')"]`);
    selectedButton.setAttribute('data-selected', 'true');
    selectedButton.classList.add('selected');

    // Store the selected option
    customerData.investmentStyle = option;
}

function handleInvestmentReaction(reaction) {
    // Deselect all buttons
    const buttons = document.querySelectorAll('#risk-fears-form .select-button');
    buttons.forEach(button => {
        button.setAttribute('data-selected', 'false');
        button.classList.remove('selected'); // Assuming you have a 'selected' class for styling
    });

    // Select the clicked button
    const selectedButton = document.querySelector(`#risk-fears-form .select-button[onclick="handleInvestmentReaction('${reaction}')"]`);
    selectedButton.setAttribute('data-selected', 'true');
    selectedButton.classList.add('selected');

    // Update the customerData object
    customerData.investmentReaction = reaction;
}

function handleCapitalPreference(preference) {
    // Deselect all buttons related to Capital Preference
    const capitalButtons = document.querySelectorAll('#capital-debt-form .goals-selection[capital-preference] .select-button');
    capitalButtons.forEach(button => {
        button.setAttribute('data-selected', 'false');
        button.classList.remove('selected');
    });

    // Select the clicked button
    const selectedButton = document.querySelector(`#capital-debt-form .goals-selection[capital-preference] .select-button[onclick*="${preference}"]`);
    selectedButton.setAttribute('data-selected', 'true');
    selectedButton.classList.add('selected');

    customerData.capitalPreference = preference;
}

function handleDebtFeeling(feeling) {
    // Deselect all buttons related to Debt Feeling
    const debtButtons = document.querySelectorAll('#capital-debt-form .goals-selection[debt-feeling] .select-button');
    debtButtons.forEach(button => {
        button.setAttribute('data-selected', 'false');
        button.classList.remove('selected');
    });

    // Select the clicked button
    const selectedButton = document.querySelector(`#capital-debt-form .goals-selection[debt-feeling] .select-button[onclick*="${feeling}"]`);
    selectedButton.setAttribute('data-selected', 'true');
    selectedButton.classList.add('selected');

    customerData.debtFeeling = feeling;
}

function handleAnticipatedChange(selection) {
    // Deselect all buttons related to Anticipated Changes
    const anticipatedButtons = document.querySelectorAll('#future-preferences-form .radio-option .select-button');
    anticipatedButtons.forEach(button => {
        button.setAttribute('data-selected', 'false');
        button.classList.remove('selected');
    });

    // Select the clicked button
    const selectedButton = document.querySelector(`#future-preferences-form .radio-option .select-button[id="${selection}"]`);
    selectedButton.setAttribute('data-selected', 'true');
    selectedButton.classList.add('selected');
}

function startExploring() {
    window.location.href = "/chat";
}


function handleCollegeDependents(selection) {
    // Deselect all buttons related to College Dependents
    const collegeButtons = document.querySelectorAll('#additional-fin-questions-form .radio-option .select-button');
    collegeButtons.forEach(button => {
        button.setAttribute('data-selected', 'false');
        button.classList.remove('selected');
    });

    // Select the clicked button
    const selectedButton = document.querySelector(`#additional-fin-questions-form .radio-option .select-button[id="${selection}"]`);
    selectedButton.setAttribute('data-selected', 'true');
    selectedButton.classList.add('selected');
}


function capturePersonalInfo() {
    const age = document.getElementById('age').value;
    const maritalStatus = document.getElementById('marital-status').value;
    const dependents = document.getElementById('dependents').value;

    if (!age || !maritalStatus || !dependents) {
        alert('Please answer all questions before proceeding.');
        return;
    }

    customerData.age = parseInt(age);
    customerData.maritalStatus = maritalStatus;
    customerData.dependents = parseInt(dependents);
    showScreen('second-screen');
}


function captureEmploymentIncome() {
    const employmentStatus = document.getElementById('employment-status').value;
    const annualIncome = document.getElementById('annual-income').value;
    const incomeSource = document.getElementById('income-source').value;

    if (!employmentStatus || !annualIncome || !incomeSource) {
        alert('Please answer all questions before proceeding.');
        return;
    }

    customerData.employmentStatus = employmentStatus;
    customerData.annualIncome = parseFloat(annualIncome);
    customerData.incomeSource = incomeSource;
    showScreen('third-screen');
}

function captureMajorExpenses() {

    let goals = document.querySelectorAll('#life-goals-form .select-button[data-selected="true"]');
    if (goals.length === 0) {
        alert('Please select at least one goal before proceeding.');
        return;
    }

    customerData.goals = Array.from(goals).map(el => el.getAttribute('data-goal'));
    showScreen('fifth-screen');
}


function captureFinancialCommitments(nextScreen) {
    const hasFinancialCommitments = document.getElementById('yes-commitments').getAttribute('data-selected') === 'true' || document.getElementById('no-commitments').getAttribute('data-selected') === 'true';
    const investmentDuration = document.getElementById('investment-duration').value;

    if (!hasFinancialCommitments || !investmentDuration) {
        alert('Please answer all questions before proceeding.');
        return;
    }

    customerData.investmentDuration = parseInt(investmentDuration);
    showScreen(nextScreen);
}


function captureInvestmentKnowledge() {
    const knowledgeRating = document.getElementById('knowledge-rating').value;

    if (!knowledgeRating) {
        alert('Please rate your investment knowledge before proceeding.');
        return;
    }

    customerData.investmentKnowledgeRating = parseInt(knowledgeRating);
    showScreen('seventh-screen');
}

function captureAnticipatedChanges() {
    const anticipatedChanges = document.getElementById('yes-college').getAttribute('data-selected') === 'true' || document.getElementById('no-college').getAttribute('data-selected') === 'true';
    const reviewFrequency = document.getElementById('review-frequency').value;

    if (!anticipatedChanges || !reviewFrequency) {
        alert('Please answer all questions before proceeding.');
        return;
    }

    customerData.anticipatedChangesNext3_5Years = document.getElementById('yes-college').getAttribute('data-selected') === 'true';
    customerData.reviewFrequency = reviewFrequency;
    showScreen('eleventh-screen');
    console.log("Submitting the following data:", customerData);
    submitOnboardingData();
}

function handleFinancialCommitmentsSelection(buttonId) {
    const yesButton = document.getElementById('yes-commitments');
    const noButton = document.getElementById('no-commitments');
    const nextButton = document.querySelector('.next-button');
    const investmentDurationElement = document.getElementById('investment-duration');

    // Reset both buttons to their default state
    yesButton.setAttribute('data-selected', 'false');
    yesButton.classList.remove('selected');
    noButton.setAttribute('data-selected', 'false');
    noButton.classList.remove('selected');

    // Update the selected button
    if (buttonId === 'yes-commitments') {
        yesButton.setAttribute('data-selected', 'true');
        yesButton.classList.add('selected');
        customerData.hasFinancialCommitments = true;
    } else {
        noButton.setAttribute('data-selected', 'true');
        noButton.classList.add('selected');
        customerData.hasFinancialCommitments = false;
    }

    // Check if all questions are answered
    if (customerData.hasFinancialCommitments !== null && investmentDurationElement.value !== "") {
        // Enable the Next button
        nextButton.removeAttribute('disabled');
    } else {
        // Disable the Next button
        nextButton.setAttribute('disabled', 'true');
    }

    customerData.financialCommitments = buttonId === 'yes-commitments' ? 'yes' : 'no';
}

function toggleSelection(buttonElement) {

    if (buttonElement.classList.contains('selected')) {
        buttonElement.classList.remove('selected');
    } else {
        buttonElement.classList.add('selected');
    }
}




function submitOnboardingData() {
    fetch('/onboarding-endpoint', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(customerData),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Network response was not ok: ${response.statusText}`);
        }
        return response.json();
    })
    .then(data => {
        // Handle the successful response data here
        console.log(data);
    })
    .catch(error => {
        console.error('There was a problem with the fetch operation:', error.message);
    });
}


