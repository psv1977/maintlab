document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("input[data-rut]").forEach((input) => {
    const feedback = document.createElement("small");
    feedback.className = "field-feedback";
    feedback.setAttribute("aria-live", "polite");
    input.insertAdjacentElement("afterend", feedback);

    input.addEventListener("input", () => {
      const compact = input.value.replace(/[^0-9kK]/g, "").toUpperCase();
      if (compact.length < 2) {
        feedback.textContent = "";
        return;
      }
      const number = compact.slice(0, -1);
      const verifier = compact.slice(-1);
      const total = [...number].reverse().reduce((sum, digit, index) => sum + Number(digit) * (index % 6 + 2), 0);
      const expected = "0123456789K"[(11 - total % 11) % 11];
      feedback.textContent = number && verifier === expected ? "RUT válido" : "El dígito verificador no coincide.";
      feedback.classList.toggle("invalid", number !== "" && verifier !== expected);
    });

    input.addEventListener("blur", () => {
      const compact = input.value.replace(/[^0-9kK]/g, "").toUpperCase();
      if (compact.length < 2) return;
      const number = compact.slice(0, -1).replace(/^0+/, "") || "0";
      input.value = Number(number).toLocaleString("es-CL").replace(/,/g, ".") + "-" + compact.slice(-1);
    });
  });
});
