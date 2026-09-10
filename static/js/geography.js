document.addEventListener("DOMContentLoaded", () => {
  const regionSelect = document.querySelector("select[name='region']");
  const comunaSelect = document.querySelector("select[name='comuna']");
  if (!regionSelect || !comunaSelect) return;

  const apiUrl = regionSelect.dataset.comunasUrl;

  regionSelect.addEventListener("change", () => {
    const regionId = regionSelect.value;
    comunaSelect.innerHTML = '<option value="">-- Seleccionar comuna --</option>';
    if (!regionId) return;
    fetch(`${apiUrl}?region_id=${regionId}`)
      .then((res) => res.json())
      .then((comunas) => {
        comunas.forEach(([id, name]) => {
          const opt = document.createElement("option");
          opt.value = id;
          opt.textContent = name;
          comunaSelect.appendChild(opt);
        });
      });
  });

  if (regionSelect.value) {
    regionSelect.dispatchEvent(new Event("change"));
  }
});
