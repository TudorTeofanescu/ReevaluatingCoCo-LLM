# CoCo Analysis: hammcnepmfbkccbhcecpkgffeimkalab

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: cs_window_eventListener_message → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/hammcnepmfbkccbhcecpkgffeimkalab/opgen_generated_files/cs_0.js
Line 741: `function f_bkg_receive_message(event) {`
Line 746: `mensagem = event.data;`
Line 747: `ary_partes = mensagem.split("<1>");`
Line 751: `altura = ary_partes[1];`

**Code:**

```javascript
// Content script - receives messages from iframe
function f_bkg_receive_message(event) {
    var ary_partes, mensagem, altura, palavra, novo_dicionario;

    // Only accept messages from trusted iframe origin
    if ((event.origin == "http://houaiss.online")||(event.origin == "https://houaiss.online")) {
        mensagem = event.data; // ← attacker-controlled (if from houaiss.online)
        ary_partes = mensagem.split("<1>");

        // Message type 1: height adjustment
        if (ary_partes[0] == 1) {
            altura = ary_partes[1]; // ← attacker-controlled
            if (altura == Number(altura)) {
                // Uses height to set iframe height (DOM manipulation only, not storage)
                if (altura < iframe_minheight) { document.getElementById("elm_dh_conteudo").style.height = "100px"; }
                else if (altura > iframe_maxheight) { document.getElementById("elm_dh_conteudo").style.height = "400px"; }
                else { document.getElementById("elm_dh_conteudo").style.height = altura + "px"; }
            }
        }
        // Message type 2: search word
        else if (ary_partes[0] == 2) {
            palavra = ary_partes[1];
            f_bkg_buscar(palavra); // Searches dictionary (reads from storage, not writes)
        }
        // Message type 3: new dictionary selection
        else if (ary_partes[0] == 3) {
            novo_dicionario = ary_partes[1];
            chrome.storage.local.set({"dicionario_bkg": novo_dicionario}); // ← Storage write
        }
    }
}

// Add event listener
window.addEventListener("message", f_bkg_receive_message, false);
```

**Classification:** FALSE POSITIVE

**Reason:** Hardcoded backend URL (trusted infrastructure). The postMessage listener only accepts messages from a hardcoded origin: `http://houaiss.online` or `https://houaiss.online`. This is the extension's own backend infrastructure (the dictionary service iframe).

Per methodology: "Hardcoded backend URLs are still trusted infrastructure. Data TO/FROM developer's own backend servers = FALSE POSITIVE. Compromising developer infrastructure is separate from extension vulnerabilities."

While technically the flow allows `houaiss.online` to write to storage (setting dictionary preference), this is by design - the extension trusts its own backend service. An attacker would need to compromise the houaiss.online domain to exploit this, which is an infrastructure issue, not an extension vulnerability. The extension correctly validates the origin before processing messages.

Additionally, the stored value `dicionario_bkg` is only a dictionary preference setting used for internal extension functionality, with no retrieval path back to any attacker-controlled destination.
