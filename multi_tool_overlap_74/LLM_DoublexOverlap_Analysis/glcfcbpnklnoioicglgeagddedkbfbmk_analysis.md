# CoCo Analysis: glcfcbpnklnoioicglgeagddedkbfbmk

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** Multiple flows (cs_window_eventListener_message → XMLHttpRequest_url_sink)

---

## Sink: cs_window_eventListener_message → XMLHttpRequest_url_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/glcfcbpnklnoioicglgeagddedkbfbmk/opgen_generated_files/cs_0.js
Line 581   window.addEventListener('message', function(event) {
Line 588     if (event.data.type && (event.data.type == "FROM_TVQUE_FOR_ROKU")) {

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/glcfcbpnklnoioicglgeagddedkbfbmk/opgen_generated_files/bg.js
Line 1078  query_app_withIPAddr(hints.ipaddress, null);
Line 1907  xhr_get.open('GET', 'http://'+glb_dev_ip+':8060/query/apps', true);
```

**Code:**

```javascript
// Content script (cs_0.js) - Only runs on *://www.tvque.com/*
window.addEventListener('message', function(event) {
  if (event.source != window)
    return;

  if (event.data.type && (event.data.type == "FROM_TVQUE_FOR_ROKU")) {
    console.log("Content script received: " + event.data.text);
    port.postMessage(event.data); // ← Send to background
    return;
  }
});

// Background script (bg.js)
function portOnMessageHandler(hints) {
  if (hints.text === "LAUNCH_ROKU_TVQUE") {
    query_app_withIPAddr(hints.ipaddress, null); // ← IP address from message
    return;
  }
}

function query_app_withIPAddr(ip_addr, name) {
  glb_dev_url = 'http://' + ip_addr + ':8888/';
  glb_dev_ip = ip_addr;
  query_app();
}

function query_app() {
  var xhr_get = new XMLHttpRequest();
  xhr_get.open('GET', 'http://' + glb_dev_ip + ':8060/query/apps', true); // ← XHR to user-controlled IP
  xhr_get.send(null);
}
```

**Classification:** FALSE POSITIVE

**Reason:** The content script only runs on the extension's own website (`*://www.tvque.com/*` per manifest.json line 29). This is not an external attacker trigger, but rather the extension's own trusted webpage communicating with its companion browser extension.

The flow is:
1. User visits www.tvque.com (extension's own website - trusted infrastructure)
2. tvque.com webpage → content script (via postMessage)
3. Content script → background script (via chrome.runtime.sendMessage)
4. Background script → User's local Roku device (on local network via IP:8060/8888)

This is the extension's designed functionality: the tvque.com website instructs the browser extension to communicate with the user's Roku TV on their local network. The "attacker-controlled" IP address is actually the user's own Roku device that they configured to use with the extension.

According to the CoCo methodology, data flows involving hardcoded backend/infrastructure URLs are FALSE POSITIVES. Here, www.tvque.com is the developer's trusted infrastructure, and only that specific domain can trigger this flow (not arbitrary external websites).
