# CoCo Analysis: lggbnokjmkbejjkfodafgnplfbpgnhdh

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 2 (both identical flows from different content scripts)

---

## Sink: cs_window_eventListener_message → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/lggbnokjmkbejjkfodafgnplfbpgnhdh/opgen_generated_files/cs_0.js
Line 477: `window.addEventListener('message', function (event) {`
Line 478: `if (event.data.type) {`
Line 480: `const value = event.data.data;`

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/lggbnokjmkbejjkfodafgnplfbpgnhdh/opgen_generated_files/bg.js
Line 972: `chrome.storage.local.set(JSON.parse(message.message.key));`

**Analysis:**
The extension accepts postMessage from web pages and stores attacker-controlled data in storage. However, according to CoCo Analysis Methodology Rule #2, storage poisoning alone is NOT a vulnerability. For TRUE POSITIVE, the stored data must flow back to the attacker.

**Code:**

```javascript
// Content script (cs_0.js, cs_1.js) - Entry point
window.addEventListener('message', function (event) {
    if (event.data.type) {
        const key = event.data.type;
        const value = event.data.data; // ← attacker-controlled
        if (["dgi_values", "can_start", "messageValues"].includes(key)) {
            console.log("message received");
            sendToStorageMessage({ key: value }); // Send to background
        }
    }
});

function sendToStorageMessage(values) {
    chrome.runtime.sendMessage(chrome.runtime.id, { "message": values }, (req, res) => {
        console.log("data retrieved");
    });
}

// Background script (bg.js) - Storage write
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    console.log(message.message.key);
    chrome.storage.local.set(JSON.parse(message.message.key)); // Storage poisoning
    sendResponse = () => {
        console.log("sended");
        return true;
    };
    return true;
});

// Content script (cs_1.js) - Storage read (but no exfiltration)
chrome.storage.local.get(["dgi_values", "can_start"]).then(async function (data) {
    // Data is used for autofilling login forms, not sent back to attacker
    if (dgi_values && (dgi_values.login || dgi_values.password)) {
        inputLogin.value = loginValue;
        inputPwd.value = atob(pwdValue);
        // ... autofill logic only
    }
});

// The only postMessage back to webpage sends comparison results (boolean), not actual data:
window.postMessage({
    type: 'can_start',
    data: JSON.stringify({ can_start: { sameIce: sameIce, sameVat: sameVat } })
}, '*');
```

**Classification:** FALSE POSITIVE

**Reason:** Incomplete storage exploitation. While the extension accepts attacker data via postMessage and stores it (storage.set), there is no retrieval path where the attacker can access this stored data. The stored data is only used internally for autofilling login forms. The only postMessage back to the webpage sends boolean comparison results, not the actual stored credentials. According to CoCo Methodology Rule #2: "Storage poisoning alone is NOT a vulnerability" - the stored value must flow back to the attacker through sendResponse, postMessage, or be used in a subsequent vulnerable operation to be TRUE POSITIVE.
