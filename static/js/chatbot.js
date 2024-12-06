// Function to submit the form data and get diagnosis
function submitForm() {
  const symptoms = document
    .getElementById("symptoms")
    .value.split(",")
    .map((item) => item.trim());
  const medicalHistory = document.getElementById("medical_history").value;
  const age = document.getElementById("age").value;
  const gender = document.getElementById("gender").value;

  // Check if symptoms and age are provided
  if (!symptoms || symptoms.length === 0 || !age) {
    alert("Please provide symptoms and age.");
    return;
  }

  const data = {
    symptoms: symptoms,
    medical_history: medicalHistory,
    age: parseInt(age),
    gender: gender,
  };

  // Call the API
  fetch("http://127.0.0.1:5000/diagnose", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  })
    .then((response) => response.json())
    .then((result) => displayResult(result))
    .catch((error) => console.error("Error:", error));
}

// Function to display the diagnosis result
function displayResult(result) {
  const resultDiv = document.getElementById("result");
  resultDiv.innerHTML = "";

  if (result.possible_conditions && result.possible_conditions.length > 0) {
    const ul = document.createElement("ul");
    result.possible_conditions.forEach((condition) => {
      const li = document.createElement("li");
      li.textContent = condition;
      ul.appendChild(li);
    });
    resultDiv.appendChild(ul);
  } else {
    resultDiv.textContent =
      "No diagnosis found. Please consult a healthcare provider.";
  }
}
