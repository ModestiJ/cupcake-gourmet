// Cupcake Gourmet – interações leves (progressive enhancement: tudo funciona sem JS).
(function () {
  "use strict";

  // Confirmação antes de ações destrutivas (RNF04 – ações reversíveis/confirmadas).
  document.addEventListener("submit", function (e) {
    var msg = e.target.getAttribute("data-confirmar");
    if (msg && !window.confirm(msg)) e.preventDefault();
  });

  // Botões +/- de quantidade.
  document.querySelectorAll("[data-qtd]").forEach(function (box) {
    var input = box.querySelector("input");
    box.querySelectorAll("button[data-passo]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var min = parseInt(input.min || "0", 10);
        var max = parseInt(input.max || "999", 10);
        var v = (parseInt(input.value, 10) || 0) + parseInt(btn.dataset.passo, 10);
        input.value = Math.max(min, Math.min(max, v));
        if (box.dataset.autoenvio !== undefined) input.form.submit();
      });
    });
  });

  // Fechar mensagens.
  document.querySelectorAll(".msg button").forEach(function (b) {
    b.addEventListener("click", function () { b.closest(".msg").remove(); });
  });

  // Checkout: mostra endereços só para entrega e recalcula o total (US16).
  var checkout = document.getElementById("form-checkout");
  if (checkout) {
    var fmt = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" });
    var subtotal = parseFloat(checkout.dataset.subtotal);
    var blocoEnd = document.getElementById("bloco-endereco");
    var elTaxa = document.getElementById("valor-taxa");
    var elTotal = document.getElementById("valor-total");
    var btn = document.getElementById("btn-finalizar");
    function atualizar() {
      var tipo = (checkout.querySelector("[name=tipo_entrega]:checked") || {}).value;
      var taxa = 0, ok = !!tipo;
      blocoEnd.hidden = tipo !== "ENTREGA";
      if (tipo === "ENTREGA") {
        var end = checkout.querySelector("[name=endereco]:checked");
        if (end && end.dataset.taxa !== "") { taxa = parseFloat(end.dataset.taxa); } else { ok = false; }
      }
      ok = ok && !!checkout.querySelector("[name=metodo_pagamento]:checked");
      elTaxa.textContent = tipo === "ENTREGA" && !ok && !checkout.querySelector("[name=endereco]:checked") ? "—" : fmt.format(taxa);
      elTotal.textContent = fmt.format(subtotal + taxa);
      btn.disabled = !ok;
    }
    checkout.addEventListener("change", atualizar);
    atualizar();
  }

  // Copiar código Pix.
  var copiar = document.getElementById("copiar-pix");
  if (copiar && navigator.clipboard) {
    copiar.addEventListener("click", function () {
      navigator.clipboard.writeText(document.getElementById("codigo-pix").textContent.trim());
      copiar.textContent = "Copiado!";
    });
  }

  // PWA
  if ("serviceWorker" in navigator) {
    window.addEventListener("load", function () { navigator.serviceWorker.register("/sw.js").catch(function () {}); });
  }
})();
