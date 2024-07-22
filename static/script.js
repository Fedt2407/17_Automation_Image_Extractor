const fileInput = document.getElementById("file-input");
const dragArea = document.getElementById("drag-area");
const dragText = document.getElementById("drag-text");
const fileInfo = document.getElementById("file-info");
const uploadForm = document.getElementById("upload-form");

// Event listener for file input change
fileInput.addEventListener("change", (event) => {
  const fileName = event.target.files[0]?.name;
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

// Handle form submission
uploadForm.addEventListener("submit", (event) => {
  event.preventDefault(); // Prevent form from submitting the default way

  // Show spinner while processing
  dragText.innerHTML = `Elaborazione in corso <i class="fas fa-spinner fa-spin"></i>`;

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
        dragText.textContent = `Estrazione immagini avvenuta con successo.`;

        // Supponiamo che tu restituisca il nome del file da scaricare nella risposta
        const filename = data.filename; // Assicurati che il tuo backend restituisca questo campo

        // Esegui la chiamata per scaricare il file
        fetch(`/download/${filename}`)
          .then((response) => {
            if (!response.ok) {
              throw new Error("Errore nel download del file");
            }
            return response.blob(); // Ottieni il file come blob
          })
          .then((blob) => {
            // Crea un URL per il blob e scarica il file
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.style.display = "none";
            a.href = url;
            a.download = filename; // Imposta il nome del file da scaricare
            document.body.appendChild(a);
            a.click(); // Simula il click per scaricare
            window.URL.revokeObjectURL(url); // Libera l'URL
            a.remove(); // Rimuovi l'elemento dal DOM
          })
          .catch((error) => {
            console.error("Error downloading file:", error);
            dragText.textContent = `Errore durante il download del file.`;
          });
      } else if (data.length === 0) {
        dragText.textContent = `Nessuna immagine presente nel file caricato.`;
      } else {
        dragText.textContent = `Nessun file selezionato.`;
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      dragText.textContent = `Errore durante l'estrazione delle immagini.`;
    });
});
