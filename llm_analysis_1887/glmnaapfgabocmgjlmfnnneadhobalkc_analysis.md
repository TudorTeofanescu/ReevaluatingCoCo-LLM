# CoCo Analysis: glmnaapfgabocmgjlmfnnneadhobalkc

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 3 (all duplicate flows with same source/sink)

---

## Sink: cs_window_eventListener_message → fetch_resource_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/glmnaapfgabocmgjlmfnnneadhobalkc/opgen_generated_files/cs_0.js
Line 471: window.addEventListener("message", (event) => {
Line 472: if (event.source !== window || !event.data.type || event.data.type !== "FROM_PAGE") {
Line 478: console.log("Endpoint received:", event.data.endpoint);

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/glmnaapfgabocmgjlmfnnneadhobalkc/opgen_generated_files/bg.js
Line 991: fetch("http://localhost:3000/"+endpoint, {

**Code:**

```javascript
// Content script (cs_0.js) - Entry point
window.addEventListener("message", (event) => {
  if (event.source !== window || !event.data.type || event.data.type !== "FROM_PAGE") {
    return;
  }

  reconnectPort();
  console.log("Content script received:", event.data.data);
  console.log("Endpoint received:", event.data.endpoint); // ← attacker-controlled

  // Send message to background.js
  if (port) {
    port.postMessage({ command: "print", data: event.data.data, endpoint: event.data.endpoint }); // ← attacker-controlled
  }
});

// Background script (bg.js) - Message handler
chrome.runtime.onConnect.addListener((port) => {
  port.onMessage.addListener((request) => {
    if (request.command === "print") {
      printToPrinter(request.endpoint, request.data); // ← attacker-controlled
    }
  });
});

// Background script - Sink
function printToPrinter(endpoint, data) {
  fetch("http://localhost:3000/"+endpoint, { // ← attacker-controlled endpoint
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ data: data }),
  })
}
```

**Classification:** FALSE POSITIVE

**Reason:** The fetch() sink sends attacker-controlled data to a hardcoded backend URL (`http://localhost:3000/`). This is the developer's trusted infrastructure. The attacker can only append to the path and control the data body sent to the localhost server, but cannot redirect the request to an attacker-controlled domain. According to the methodology, data TO/FROM hardcoded developer backend URLs is considered trusted infrastructure, making this a FALSE POSITIVE. Compromising localhost:3000 would be an infrastructure issue, not an extension vulnerability.
