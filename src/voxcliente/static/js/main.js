// VoxCliente - Simplified Frontend JavaScript
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
      let validationMessage = "Por favor completa todos los campos:";
      if (!email) validationMessage += "\n• Ingresa tu email";
      if (!file) validationMessage += "\n• Selecciona un archivo de audio";
      if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email))
        validationMessage += "\n• Email inválido";

      showNotification(validationMessage, "error");
      return;
    }

    // Estado de carga mejorado con feedback visual en el formulario
    submitBtn.disabled = true;
    submitBtn.classList.add("opacity-75", "cursor-not-allowed");

    // Agregar indicador visual al formulario
    const formCard = uploadForm.closest(".rounded-lg");
    formCard.classList.add("processing");
    formCard.style.position = "relative";

    // Crear overlay de procesamiento en el formulario
    const processingOverlay = document.createElement("div");
    processingOverlay.className =
      "absolute inset-0 bg-white/80 backdrop-blur-sm rounded-lg flex items-center justify-center z-10";
    processingOverlay.innerHTML = `
      <div class="text-center">
        <div class="w-16 h-16 bg-gradient-primary rounded-full flex items-center justify-center mx-auto mb-4 animate-pulse">
          <svg class="w-8 h-8 text-primary-foreground animate-spin" viewBox="0 0 24 24" fill="none">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        </div>
        <h3 class="text-lg font-semibold text-foreground mb-2">Procesando tu audio</h3>
        <p class="text-sm text-muted-foreground">Nuestra IA está transcribiendo y generando las actas...</p>
        <p class="text-xs text-muted-foreground mt-2">⏱️ Esto puede tardar hasta 10 minutos dependiendo del tamaño del archivo</p>
        <div class="flex justify-center gap-1 mt-4">
          <div class="w-2 h-2 bg-primary rounded-full animate-bounce" style="animation-delay: 0ms"></div>
          <div class="w-2 h-2 bg-primary rounded-full animate-bounce" style="animation-delay: 150ms"></div>
          <div class="w-2 h-2 bg-primary rounded-full animate-bounce" style="animation-delay: 300ms"></div>
        </div>
      </div>
    `;
    formCard.appendChild(processingOverlay);

    submitBtn.innerHTML = `
      <div class="flex items-center justify-center gap-3">
        <div class="relative">
          <svg class="animate-spin w-5 h-5" viewBox="0 0 24 24" fill="none">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        </div>
        <span class="font-medium">Procesando con IA...</span>
        <div class="flex gap-1">
          <div class="w-1 h-1 bg-current rounded-full animate-bounce" style="animation-delay: 0ms"></div>
          <div class="w-1 h-1 bg-current rounded-full animate-bounce" style="animation-delay: 150ms"></div>
          <div class="w-1 h-1 bg-current rounded-full animate-bounce" style="animation-delay: 300ms"></div>
        </div>
      </div>
    `;

    try {
      const formData = new FormData();
      formData.append("email", email);
      formData.append("file", file);

      const response = await fetch("/api/v1/transcribe", {
        method: "POST",
        body: formData,
        signal: AbortSignal.timeout(600000), // 10 minutos timeout
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.detail || `Error: ${response.status} ${response.statusText}`
        );
      }

      // Respuesta exitosa mejorada
      const responseData = await response.json().catch(() => ({}));
      const fileName = audioFileInput.files[0]?.name || "tu archivo";

      // Descargar archivos automáticamente si están disponibles
      if (responseData.download_files) {
        try {
          await downloadFile(
            responseData.download_files.acta_url,
            responseData.download_files.acta_filename
          );

          await downloadFile(
            responseData.download_files.transcript_url,
            responseData.download_files.transcript_filename
          );

          showNotification(
            `¡Listo! Tu acta profesional ya está descargada en tu dispositivo. Los archivos Word están listos para usar. También enviamos una copia por email (revisa spam si no la ves).`,
            "success"
          );
        } catch (downloadError) {
          console.error("Error descargando archivos:", downloadError);
          showNotification(
            `¡Perfecto! Hemos procesado "${fileName}" exitosamente. Las actas profesionales llegarán a ${email} en los próximos minutos.`,
            "success"
          );
        }
      } else {
        showNotification(
          `¡Perfecto! Hemos procesado "${fileName}" exitosamente. Las actas profesionales llegarán a ${email} en los próximos minutos.`,
          "success"
        );
      }

      // Limpiar formulario con animación
      setTimeout(() => {
        uploadForm.reset();
        updateFileDisplay(true);
      }, 1000);
    } catch (error) {
      console.error("Error:", error);

      // Manejo de errores más específico
      let errorMessage = "Error al procesar el archivo";

      if (
        error.message.includes("413") ||
        error.message.includes("too large")
      ) {
        errorMessage =
          "El archivo es demasiado grande. Por favor, sube un archivo de máximo 150MB.";
      } else if (
        error.message.includes("415") ||
        error.message.includes("unsupported")
      ) {
        errorMessage =
          "Formato de archivo no soportado. Usa MP3, WAV, M4A, MP4 u OGG.";
      } else if (error.message.includes("400")) {
        errorMessage =
          "Datos inválidos. Verifica tu email y el archivo de audio.";
      } else if (error.message.includes("500")) {
        errorMessage =
          "Error interno del servidor. Por favor, intenta nuevamente en unos minutos.";
      } else if (
        error.message.includes("NetworkError") ||
        error.message.includes("fetch")
      ) {
        errorMessage =
          "Error de conexión. Verifica tu internet e intenta nuevamente.";
      } else if (
        error.message.includes("524") ||
        error.message.includes("timeout")
      ) {
        errorMessage =
          "El procesamiento tardó más de lo esperado. Tu archivo se está procesando en segundo plano. Revisa tu email en unos minutos.";
      } else {
        errorMessage = `Error al procesar el archivo: ${error.message}`;
      }

      showNotification(errorMessage, "error");
    } finally {
      // Limpiar overlay del formulario
      const processingOverlay = formCard.querySelector(".absolute.inset-0");
      if (processingOverlay) {
        processingOverlay.remove();
      }
      formCard.classList.remove("processing");

      // Restaurar botón con animación suave
      submitBtn.disabled = false;
      submitBtn.classList.remove("opacity-75", "cursor-not-allowed");
      submitBtn.innerHTML = `
        <div class="flex items-center justify-center gap-2">
          <span class="font-medium">Procesar Audio</span>
          <svg class="w-4 h-4 transition-transform duration-200" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M5 12h14"></path>
            <path d="m12 5 7 7-7 7"></path>
          </svg>
        </div>
      `;
      validateForm();
    }
  });

  // Mostrar notificación mejorada - centrada y más visible
  function showNotification(message, type = "info") {
    const colors = {
      success:
        "background: linear-gradient(135deg, hsl(142 76% 36%), hsl(142 76% 30%)); color: white; border: 2px solid hsl(142 76% 20%);",
      error:
        "background: linear-gradient(135deg, hsl(0 84% 60%), hsl(0 84% 50%)); color: white; border: 2px solid hsl(0 84% 40%);",
      info: "background: linear-gradient(135deg, hsl(var(--primary)), hsl(var(--primary) / 0.8)); color: white; border: 2px solid hsl(var(--primary) / 0.6);",
    };

    const icons = {
      success:
        '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22,4 12,14.01 9,11.01"></polyline>',
      error:
        '<circle cx="12" cy="12" r="10"></circle><line x1="15" x2="9" y1="9" y2="15"></line><line x1="9" x2="15" y1="9" y2="15"></line>',
      info: '<circle cx="12" cy="12" r="10"></circle><path d="M12 16v-4"></path><path d="M12 8h.01"></path>',
    };

    // Crear overlay de fondo
    const overlay = document.createElement("div");
    overlay.className = "notification-overlay";
    overlay.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      background: rgba(0, 0, 0, 0.2);
      backdrop-filter: blur(4px);
      z-index: 40;
      opacity: 0;
      transition: opacity 0.3s ease;
    `;

    // Crear notificación centrada
    const notification = document.createElement("div");
    notification.className = "notification-modal";
    notification.style.cssText = `
      position: fixed;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      z-index: 50;
      padding: 1.5rem;
      border-radius: 1rem;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
      max-width: 28rem;
      width: calc(100vw - 2rem);
      margin: 0 1rem;
      transition: all 0.3s ease;
      transform: translate(-50%, -50%) scale(0.75);
      opacity: 0;
      ${colors[type]}
    `;
    notification.innerHTML = `
      <div class="text-center">
        <div class="flex items-center justify-center mb-4">
          <div class="w-16 h-16 rounded-full bg-white/20 flex items-center justify-center">
            <svg class="w-8 h-8" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              ${icons[type]}
            </svg>
          </div>
        </div>
        <h3 class="text-xl font-bold mb-2">${
          type === "success"
            ? "¡Éxito!"
            : type === "error"
            ? "Error"
            : "Información"
        }</h3>
        <p class="text-sm leading-relaxed mb-4">${message}</p>
        <button class="px-6 py-2 bg-white/20 hover:bg-white/30 rounded-lg font-medium transition-colors duration-200" onclick="closeNotification(this)">
          Entendido
        </button>
      </div>
    `;

    // Prevenir scroll del body
    document.body.classList.add("notification-open");

    document.body.appendChild(overlay);
    document.body.appendChild(notification);

    // Animar entrada
    setTimeout(() => {
      overlay.style.opacity = "1";
      notification.style.transform = "translate(-50%, -50%) scale(1)";
      notification.style.opacity = "1";
    }, 100);

    // Auto-cerrar después de 8 segundos
    setTimeout(() => {
      overlay.style.opacity = "0";
      notification.style.transform = "translate(-50%, -50%) scale(0.75)";
      notification.style.opacity = "0";
      setTimeout(() => {
        if (document.body.contains(overlay)) document.body.removeChild(overlay);
        if (document.body.contains(notification))
          document.body.removeChild(notification);
        document.body.classList.remove("notification-open");
      }, 300);
    }, 8000);
  }

  // Initialize form validation
  validateForm();
});

// Función para descargar archivos automáticamente
async function downloadFile(url, filename) {
  try {
    console.log(`Iniciando descarga: ${url} como ${filename}`);

    const response = await fetch(url);

    if (!response.ok) {
      throw new Error(
        `Error descargando archivo: ${response.status} ${response.statusText}`
      );
    }

    const blob = await response.blob();

    // Crear URL temporal para descarga
    const downloadUrl = URL.createObjectURL(blob);

    // Crear elemento de descarga temporal
    const a = document.createElement("a");
    a.href = downloadUrl;
    a.download = filename;
    a.style.display = "none";

    // Agregar al DOM, hacer clic y remover
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);

    // Limpiar URL temporal
    URL.revokeObjectURL(downloadUrl);

    console.log(`Descarga completada: ${filename}`);
  } catch (error) {
    console.error(`Error descargando ${filename}:`, error);
    throw error;
  }
}

// Función global para cerrar notificaciones
function closeNotification(button) {
  const notification = button.closest(".notification-modal");
  const overlay = document.querySelector(".notification-overlay");

  if (notification) {
    notification.style.transform = "translate(-50%, -50%) scale(0.75)";
    notification.style.opacity = "0";
  }

  if (overlay) {
    overlay.style.opacity = "0";
  }

  setTimeout(() => {
    if (notification && document.body.contains(notification)) {
      document.body.removeChild(notification);
    }
    if (overlay && document.body.contains(overlay)) {
      document.body.removeChild(overlay);
    }
    document.body.classList.remove("notification-open");
  }, 300);
}
