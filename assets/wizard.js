let currentStep = 1;
const totalSteps = 6;

const steps = document.querySelectorAll(".wizard-step");
const nextBtn = document.getElementById("nextBtn");
const prevBtn = document.getElementById("prevBtn");
const stepIndicator = document.getElementById("step-indicator");

function updateStepView() {
  steps.forEach((step) => {
    step.style.display = parseInt(step.dataset.step) === currentStep ? "block" : "none";
  });

  stepIndicator.textContent = `Paso ${currentStep} de ${totalSteps}`;
  prevBtn.disabled = currentStep === 1;
  nextBtn.style.display = currentStep === totalSteps ? "none" : "inline-block";
}

nextBtn.addEventListener("click", () => {
  if (currentStep < totalSteps) {
    currentStep++;
    updateStepView();
  }
});

prevBtn.addEventListener("click", () => {
  if (currentStep > 1) {
    currentStep--;
    updateStepView();
  }
});

document.addEventListener("DOMContentLoaded", updateStepView);
function calcularPerfilFinanciero() {
    const tipoIngresos = document.getElementById("tipoIngresos").value;
    const ingresos = document.getElementById("rangoIngresos").value;
    const edad = document.getElementById("edad").value;
  
    let perfil = "medio"; // por defecto
  
    const ingresosNum = ingresos.includes("+")
      ? 60
      : ingresos.includes("<")
      ? 5
      : parseInt(ingresos.split("-")[0]);
  
    const edadNum = parseInt(edad.split("-")[0]);
  
    if (
      (tipoIngresos === "Comprobables 100%" || tipoIngresos === "Comprobable 75%") &&
      ingresosNum >= 30 &&
      edadNum < 55
    ) {
      perfil = "alto";
    } else if (
      (tipoIngresos === "Comprobable 50%" || tipoIngresos === "Comprobable 25%") &&
      ingresosNum >= 15 &&
      ingresosNum <= 30 &&
      edadNum < 60
    ) {
      perfil = "medio";
    } else if (tipoIngresos === "Informal" || ingresosNum < 15) {
      perfil = "bajo";
    }
  
    const texto = {
      alto: "💼 Perfil Alto (ingreso alto, comprobable, riesgo bajo)",
      medio: "🧾 Perfil Medio (ingreso medio, parcialmente comprobable)",
      bajo: "⚠️ Perfil Bajo (ingreso bajo o informal, riesgo alto)",
    };
  
    document.getElementById("perfilCalculado").innerText = texto[perfil];
    // Guardamos en hidden input (útil para el cálculo final)
    document.getElementById("perfilCalculado").dataset.perfil = perfil;
  }
  