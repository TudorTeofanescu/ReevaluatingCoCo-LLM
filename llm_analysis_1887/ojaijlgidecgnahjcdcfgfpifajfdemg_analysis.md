# CoCo Analysis: ojaijlgidecgnahjcdcfgfpifajfdemg

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: cs_window_eventListener_message → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ojaijlgidecgnahjcdcfgfpifajfdemg/opgen_generated_files/cs_0.js
Line 596: function onWindowEvent(event) { event }
Line 600: var data = event.data
Line 613: notifyAuthComplete(data.params.authToken);
Line 613: data.params
Line 613: data.params.authToken

**Code:**

```javascript
// Content script (cs_0.js)
flaunt.bindWindowEventListener = function(extensionId, chromeExtensionOrigin) {

  function notifyAuthComplete(authToken) {
    // Send authToken to background script
    chrome.extension.sendMessage({
      action: flaunt.events.AUTH_COMPLETE,
      authToken: authToken  // ← attacker-controlled
    }, function(response) { })
  }

  function onWindowEvent(event) {
    if (event.origin != chromeExtensionOrigin) {  // Origin check present
      return
    }
    var data = event.data  // ← attacker-controlled
    if (data.src != 'flaunt') {
      return
    }

    if (data.action == 'flaunt_frame_ready') {
      flaunt.ui.initialiseFrameView()
    } else if (data.extensionId == extensionId) {
      var action = data.action
      if (action == "flaunt_close") {
        flaunt.ui.closeFlauntFrame()
      } else if (action == "flaunt_auth") {
        flaunt.ui.closeFlauntFrame();
        notifyAuthComplete(data.params.authToken);  // ← attacker-controlled
      } else if (action == "flaunt_form_success") {
        flaunt.ui.state.submitted = true
        closeIfReady()
      }
    }
  }

  window.addEventListener("message", onWindowEvent);  // ← entry point
}

var chromeExtensionOrigin = "chrome-extension://" + chrome.i18n.getMessage("@@extension_id")
var extensionId = chrome.i18n.getMessage("@@extension_id")
flaunt.setupEventListeners(extensionId, chromeExtensionOrigin)

// Background script (bg.js)
flaunt.AuthTokenSupport = function() {
  this.setAuthToken = function(newKey, callback) {
    chrome.storage.local.set({flauntKey: newKey}, function() {  // ← sink
      callback();
    })
  }
}

var auth = new flaunt.AuthTokenSupport();

chrome.extension.onMessage.addListener(function(request, sender, sendResponse) {
  var action = request.action
  if (action == flaunt.events.REQUEST_SCREENSHOT) {
    // ... screenshot handling
  } else if (action == flaunt.events.START) {
    controller.start(request.tabId)
  } else if (action == flaunt.events.AUTH_COMPLETE) {
    auth.setAuthToken(request.authToken, function() {  // ← attacker-controlled authToken stored
      controller.start(sender.tab)
    });
  } else if (action == flaunt.events.CONTENT_SCRIPT_LOADED) {
    // ... content script loaded handling
  }
  return true;
});
```

**Classification:** FALSE POSITIVE

**Reason:** The stored authentication token (flauntKey) is retrieved and sent to the hardcoded backend URL `https://flauntreport.com/ce/flauntlets/new.json` as the `auth_token` parameter. According to the methodology, "Storage to hardcoded backend: `storage.get → fetch('https://api.myextension.com')` = FALSE POSITIVE" because this is the developer's trusted infrastructure, not an attacker-controlled destination.
