# CoCo Analysis: aigcbpaaeflggbfikokmkkfecnlcodoh

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 2 (same vulnerability pattern)

---

## Sink: document_eventListener_updateAddressEvent → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/aigcbpaaeflggbfikokmkkfecnlcodoh/opgen_generated_files/cs_0.js
Line 498: `document.addEventListener('updateAddressEvent', function(event) {`
Line 507: `console.log('content.js - Received info of address change:', event.detail);`
Line 512-513: `assignedAddress: event.detail.assignedAddress, assignedKey: event.detail.assignedKey`

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/aigcbpaaeflggbfikokmkkfecnlcodoh/opgen_generated_files/bg.js
Line 989-990: `saveData("assignedKey", message.assignedKey); saveData("assignedAddress", message.assignedAddress);`
Line 1050: `chrome.storage.local.set({[key]: value}, ...)`

**Code:**

```javascript
// Content script - content.js (Line 470-484)
function checkDomain() {
  if (window.location.protocol === "https:" && window.location.hostname === "temporarymail.com") {
    return true;
  } else {
    return false;
  }
}

// Content script - content.js (Line 498-517)
document.addEventListener('updateAddressEvent', function(event) {
  if(!checkDomain()){
    console.log("Security check stopped the function from going through");
    return false;
  }

  console.log('content.js - Received info of address change:', event.detail);

  chrome.runtime.sendMessage({
    action: "updateAddress",
    assignedAddress: event.detail.assignedAddress, // ← attacker-controlled
    assignedKey: event.detail.assignedKey // ← attacker-controlled
  });
});

// Background script - background.js (Line 972-1000)
if(message.action == "updateAddress"){
  if(!message.assignedKey || !message.assignedAddress){
    console.log("aborting update as null exists");
    return true;
  }

  loadData(['assignedKey', 'assignedAddress'], function(savedData) {
    if(savedData.assignedKey != message.assignedKey || savedData.assignedAddress != message.assignedAddress){
      saveData("assignedKey", message.assignedKey); // ← storage write
      saveData("assignedAddress", message.assignedAddress); // ← storage write
      // ...
    }
  });
}

// Background script - background.js (Line 1049-1053)
function saveData(key, value) {
  chrome.storage.local.set({[key]: value}, function() {
    console.log('Value is set to ', value);
  });
}

// Storage retrieval and usage - background.js (Line 1176-1182)
fetch("https://temporarymail.com/extension/api/check/", { // ← hardcoded backend URL
  method: 'POST',
  body: JSON.stringify({
    s: savedData.assignedKey, // ← poisoned data sent to backend
    k: keysDictionary
  })
})
```

**Classification:** FALSE POSITIVE

**Reason:** While an attacker can poison storage via `document.addEventListener` (custom DOM event), the stored data (assignedKey and assignedAddress) is only sent to a hardcoded developer backend URL (`https://temporarymail.com/extension/api/check/`). According to the methodology, data flowing to hardcoded developer backend URLs is considered trusted infrastructure, not an extension vulnerability. The checkDomain() validation adds another layer but per methodology, manifest restrictions should be ignored when analyzing DOM event listeners. However, the ultimate classification is FALSE POSITIVE because the data goes to trusted backend infrastructure.
