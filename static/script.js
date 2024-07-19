const fileInput = document.getElementById("file-input");
const dragArea = document.getElementById("drag-area");
const dragText = document.getElementById("drag-text");
const fileInfo = document.getElementById("file-info");
const uploadForm = document.getElementById("upload-form");

// Event listener for file input change
fileInput.addEventListener("change", (event) => {
  const fileName = event.target.files[0].name;
  dragText.textContent = `File selezionato: ${fileName}`;
});

// Prevent default drag behaviors
["dragenter", "dragover", "dragleave", "drop"].forEach((eventName) => {
  dragArea.addEventListener(eventName, preventDefaults, false);
  document.body.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults(e) {
  e.preventDefault();
  e.stopPropagation();
}

// Highlight drag area when item is dragged over it
["dragenter", "dragover"].forEach((eventName) => {
  dragArea.addEventListener(
    eventName,
    () => dragArea.classList.add("highlight"),
    false
  );
});

["dragleave", "drop"].forEach((eventName) => {
  dragArea.addEventListener(
    eventName,
    () => dragArea.classList.remove("highlight"),
    false
  );
});

// Handle dropped files
dragArea.addEventListener("drop", (event) => {
  const file = event.dataTransfer.files[0];
  fileInput.files = event.dataTransfer.files; // Set files to file input
  dragText.textContent = `File selezionato: ${file.name}`;
});

// Remove the file info message after upload
uploadForm.addEventListener("submit", (event) => {
  event.preventDefault(); // Prevent form from submitting the default way

  // Create a FormData object to send the file via fetch
  const formData = new FormData(uploadForm);

  // Send the file using fetch
  fetch(uploadForm.action, {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      // Update the UI with the response
      if (data.success) {
        dragText.textContent = `Estrazione immagini da avvenuta con successo.`;

        setTimeout(() => {
          fileInfo.innerHTML = "";
          dragText.textContent = "Trascina il PDF";
          fileInput.value = ""; // Clear the file input
          location.reload(); // Reload the page to reset the form
        }, 5000); // Clear the message after 5 seconds
      } else {
        fileInfo.innerHTML = "<p>Failed to upload file.</p>";
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      fileInfo.innerHTML = "<p>An error occurred while uploading the file.</p>";
    });
});
