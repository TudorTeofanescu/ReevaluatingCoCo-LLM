# CoCo Analysis: pommbdemknolomeklfmebpakogompihb

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1 (chrome_storage_local_set_sink)

---

## Sink: document_body_innerText → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/pommbdemknolomeklfmebpakogompihb/opgen_generated_files/cs_0.js
Line 29: Document_element.prototype.innerText = new Object();

CoCo referenced only framework code (CoCo header before line 465). Checking actual extension code:

**Code:**

```javascript
// Content script - Automatic extraction (cs_0.js lines 467-476)
console.log("Extension Sign Language NG");
function extraerTexto() {
  var texto = document.body.innerText;  // ← webpage content (not attacker-controlled)
  console.log(texto);

  // Enviar texto al script de fondo
  chrome.runtime.sendMessage({ texto: texto });  // ← send to background
}

extraerTexto();

// Background script - Storage write (bg.js lines 1005-1012)
chrome.runtime.onMessage.addListener(
  function(request, sender, sendResponse) {
    if(request.texto) {
      // Guardar en el almacenamiento local
      chrome.storage.local.set({selectedText: request.texto}, function() {
        console.log('Texto seleccionado guardado: ' + request.texto);
      });
    }
    // ... context menu handler also saves to storage
  }
);
```

**Classification:** FALSE POSITIVE

**Reason:** Storage poisoning without retrieval path. The extension reads document.body.innerText and stores it, but there is no code path where the stored data flows back to an attacker-accessible output (no sendResponse, no postMessage, no fetch to attacker URL). The data is only stored and never retrieved for attacker access.
