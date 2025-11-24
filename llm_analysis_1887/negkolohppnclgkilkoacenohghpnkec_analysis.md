# CoCo Analysis: negkolohppnclgkilkoacenohghpnkec

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: cs_window_eventListener_message → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/negkolohppnclgkilkoacenohghpnkec/opgen_generated_files/cs_0.js
Line 496	(printInput) => {
Line 498	!printInput.data.type ||
Line 524	zpl: printInput.data.zpl,

**Code:**

```javascript
// Content script (cs_0.js) - Lines 494-527
window.addEventListener(
  "message",
  (printInput) => {  // ← attacker-controlled via postMessage
    if (
      !printInput.data.type ||
      printInput.data.type != "vm_zebra_print_label"
    ) {
      return;
    }
    chrome.storage.local.get(["currentIp"], function (result) {
      if (result.currentIp && result.currentIp.length > 0) {
        chrome.storage.local.get(["availableIpsWithHtml"], (res) => {
          // ... validation code ...
          const data = {
            zpl: printInput.data.zpl,  // ← attacker-controlled
            url: result.currentIp + "/pstprnt",  // ← from storage (printer IP)
          };
          chrome.runtime.sendMessage(data, function (response) {
            // ... response handling ...
          });
        });
      }
    });
  }
);

// Background (bg.js) - Lines 997-1030
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (!message.url) {
    return;
  }
  // Sends attacker-controlled zpl to printer IP
  sendRequest(message.url, message.zpl)  // ← message.zpl is attacker-controlled
    .then((response) =>
      response.status === 200
        ? sendResponse({ type: "vm_print_success" })
        : sendResponse({ type: "vm_print_error" })
    )
    .catch((exp) => console.error(exp));

  if (isChecked) {
    chrome.storage.local.get(["lastTenPrints"], function (result) {
      const prints = result.lastTenPrints || [];
      if (prints.length === 10) {
        prints.shift();
        prints.push(message);  // ← stores entire message (with zpl)
      } else {
        prints.push(message);
      }
      chrome.storage.local.set(
        {
          lastTenPrints: prints,  // ← storage poisoning
        },
        (response) => {
          chrome.runtime.sendMessage({
            type: "vm_change_print_checkbox",
          });
        }
      );
    });
  }
  return true;
});

// Lines 1158-1164
const sendRequest = async (url, data) => {
  const response = await fetch(url, {  // ← url from storage, data is attacker-controlled
    method: "POST",
    body: data,
  });
  return response;
};
```

**Classification:** FALSE POSITIVE

**Reason:** Storage poisoning only - the attacker-controlled zpl data is stored in lastTenPrints but never retrieved or sent back to the attacker. The fetch() sends data to a printer IP from storage, which is trusted infrastructure for this printer extension.
