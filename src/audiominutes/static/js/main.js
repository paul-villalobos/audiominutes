// AudioMinutes - Simplified Frontend JavaScript
document.addEventListener("DOMContentLoaded", function () {
  const uploadForm = document.getElementById("upload-form");
  const emailInput = document.getElementById("email");
  const audioFileInput = document.getElementById("audio-file");
  const dropZone = document.getElementById("drop-zone");
  const submitBtn = document.getElementById("submit-btn");

  // Validar formulario
  function validateForm() {
    const email = emailInput.value.trim();
    const file = audioFileInput.files[0];
    const isValid = email && file && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

    submitBtn.disabled = !isValid;
    submitBtn.classList.toggle("opacity-50", !isValid);
    submitBtn.classList.toggle("hover:shadow-glow", isValid);
  }

  // Drag & Drop y eventos de archivo
  dropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropZone.classList.add("drag-over");
  });
  dropZone.addEventListener("dragleave", (e) => {
    e.preventDefault();
    dropZone.classList.remove("drag-over");
  });
  dropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropZone.classList.remove("drag-over");
    if (e.dataTransfer.files.length > 0) {
      audioFileInput.files = e.dataTransfer.files;
      updateFileDisplay();
      validateForm();
    }
  });
  dropZone.addEventListener("click", () => audioFileInput.click());
  audioFileInput.addEventListener("change", () => {
    updateFileDisplay();
    validateForm();
  });
  emailInput.addEventListener("input", validateForm);

  // Actualizar display de archivo
  function updateFileDisplay(reset = false) {
    if (reset) {
      dropZone.innerHTML = `
        <div class="space-y-2">
          <svg class="w-12 h-12 text-muted-foreground mx-auto animate-bounce-gentle" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
            <polyline points="17 8 12 3 7 8"></polyline>
            <line x1="12" x2="12" y1="3" y2="15"></line>
          </svg>
          <p class="font-medium text-foreground">Arrastra tu archivo aquí o haz click para seleccionar</p>
          <p class="text-sm text-muted-foreground">MP3, WAV, M4A, MP4, OGG - Máximo 150MB</p>
        </div>
      `;
      return;
    }

    const file = audioFileInput.files[0];
    if (file) {
      dropZone.innerHTML = `
        <div class="space-y-2">
          <div class="flex items-center justify-center gap-2">
            <svg class="w-6 h-6 text-accent" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"></path>
              <polyline points="14,2 14,8 20,8"></polyline>
            </svg>
            <span class="font-medium text-foreground">${file.name}</span>
          </div>
          <p class="text-sm text-muted-foreground">${formatFileSize(
            file.size
          )}</p>
        </div>
      `;
    }
  }

  // Formatear tamaño de archivo
  function formatFileSize(bytes) {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  }

  // Envío del formulario
  uploadForm.addEventListener("submit", async function (e) {
    e.preventDefault();
    const email = emailInput.value.trim();
    const file = audioFileInput.files[0];

    if (!email || !file || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      showNotification(
        "Por favor completa todos los campos correctamente",
        "error"
      );
      return;
    }

    // Estado de carga
    submitBtn.disabled = true;
    submitBtn.innerHTML = `
      <svg class="animate-spin w-4 h-4 mr-2" viewBox="0 0 24 24" fill="none">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      Procesando...
    `;

    try {
      const formData = new FormData();
      formData.append("email", email);
      formData.append("audio_file", file);

      const response = await fetch("/api/v1/upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.detail || `Error: ${response.status} ${response.statusText}`
        );
      }

      showNotification(
        "¡Archivo procesado exitosamente! Revisa tu email para recibir las actas.",
        "success"
      );
      uploadForm.reset();
      updateFileDisplay(true);
    } catch (error) {
      console.error("Error:", error);
      showNotification(
        "Error al procesar el archivo: " + error.message,
        "error"
      );
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = `
        Procesar Audio
        <svg class="w-4 h-4 ml-2" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M5 12h14"></path>
          <path d="m12 5 7 7-7 7"></path>
        </svg>
      `;
      validateForm();
    }
  });

  // Mostrar notificación
  function showNotification(message, type = "info") {
    const colors = {
      success: "background: hsl(142 76% 36%); color: white",
      error: "background: hsl(0 84% 60%); color: white",
      info: "background: hsl(var(--primary)); color: white",
    };

    const icons = {
      success:
        '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22,4 12,14.01 9,11.01"></polyline>',
      error:
        '<circle cx="12" cy="12" r="10"></circle><line x1="15" x2="9" y1="9" y2="15"></line><line x1="9" x2="15" y1="9" y2="15"></line>',
      info: '<circle cx="12" cy="12" r="10"></circle><path d="M12 16v-4"></path><path d="M12 8h.01"></path>',
    };

    const notification = document.createElement("div");
    notification.className =
      "fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg max-w-sm transition-all duration-300 transform translate-x-full";
    notification.style.cssText = colors[type];
    notification.innerHTML = `
      <div class="flex items-center gap-2">
        <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          ${icons[type]}
        </svg>
        <span class="font-medium">${message}</span>
      </div>
    `;

    document.body.appendChild(notification);
    setTimeout(() => notification.classList.remove("translate-x-full"), 100);
    setTimeout(() => {
      notification.classList.add("translate-x-full");
      setTimeout(() => document.body.removeChild(notification), 300);
    }, 5000);
  }

  // Initialize form validation
  validateForm();
});
