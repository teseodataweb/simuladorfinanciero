const lotesContainer = document.getElementById("lotesContainer");
const planoContainer = document.getElementById("planoContainer");

let escala = 1;
let loteActivo = null;

// Tamaño real de la imagen del plano
const planoWidth = 2859;
const planoHeight = 1230;

function aplicarZoom(factor) {
  escala *= factor;
  escala = Math.max(0.5, Math.min(escala, 3));
  planoContainer.style.transform = `scale(${escala})`;
}

document.getElementById("zoomIn").addEventListener("click", () => aplicarZoom(1.2));
document.getElementById("zoomOut").addEventListener("click", () => aplicarZoom(0.8));



// Ctrl para tooltips
window.ctrlPressed = false;
window.addEventListener("keydown", (e) => {
  if (e.key === "Control") {
    window.ctrlPressed = true;
    document.body.classList.add("ctrl-hover");
  }
});
window.addEventListener("keyup", (e) => {
  if (e.key === "Control") {
    window.ctrlPressed = false;
    document.body.classList.remove("ctrl-hover");
  }
});

// Renderizar lotes
fetch("lotes.json")
  .then((res) => res.json())
  .then((data) => {
    data.lotes.forEach((lote) => {
      const div = document.createElement("div");
      const precio = lote.valor ? `$${lote.valor.toLocaleString()}` : "N/D";

      // Convertimos coordenadas absolutas en porcentajes
      const xPercent = (parseInt(lote.coordenadasFisicas.x) / planoWidth) * 100;
      const yPercent = (parseInt(lote.coordenadasFisicas.y) / planoHeight) * 100;

      div.className = `lote ${lote.estado.replace(/ /g, "-").toLowerCase()}`;
      div.style.left = `${xPercent}%`;
      div.style.top = `${yPercent}%`;
      div.textContent = lote.id;

      div.setAttribute(
        "data-tooltip",
        `${lote.id}\nÁrea: ${lote.area} m2\nPrecio: ${precio}\nEstado: ${lote.estado.toUpperCase()}`
      );

      div.addEventListener("mouseenter", () => {
        if (div !== loteActivo) div.classList.add("mostrar-tooltip");
      });
      div.addEventListener("mouseleave", () => {
        if (div !== loteActivo) div.classList.remove("mostrar-tooltip");
      });

      div.addEventListener("click", () => {
        if (loteActivo === div) {
          div.classList.remove("mostrar-tooltip");
          loteActivo = null;
        } else {
          document.querySelectorAll(".lote").forEach((el) =>
            el.classList.remove("mostrar-tooltip")
          );
          div.classList.add("mostrar-tooltip");
          loteActivo = div;
        }
        seleccionarLote(lote);
      });

      lotesContainer.appendChild(div);
    });

    const previo = localStorage.getItem("ultimoLoteSeleccionado");
    if (previo) {
      const el = [...document.querySelectorAll(".lote")].find(
        (e) => e.textContent === previo
      );
      if (el) el.classList.add("seleccionado");
    }
  });

function seleccionarLote(lote) {
  document.querySelectorAll(".lote").forEach((l) =>
    l.classList.remove("seleccionado")
  );
  const actual = [...document.querySelectorAll(".lote")].find(
    (e) => e.textContent === lote.id
  );
  if (actual) actual.classList.add("seleccionado");

  localStorage.setItem("ultimoLoteSeleccionado", lote.id);
  const historial = JSON.parse(localStorage.getItem("historialLotes") || "[]");
  historial.push({ lote: lote.id, fecha: new Date().toISOString() });
  localStorage.setItem("historialLotes", JSON.stringify(historial));

  if (typeof calculadora !== "undefined") {
    calculadora.setLote({
      id: lote.id,
      valor: lote.valor,
      tipo: lote.tipo,
    });
  }
}
