# CoCo Analysis: jbeegkljbamjjhemcgcijglmefnhjail

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 2 (same flow, different fields)

---

## Sink: cs_window_eventListener_message → chrome_storage_local_set_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/jbeegkljbamjjhemcgcijglmefnhjail/opgen_generated_files/cs_1.js
Line 475	window.addEventListener('message', function (event) {
Line 477	if (event.data.type && event.data.type === 'loginSuccess') {
Line 478	sendDataToBackground(event.data.payload);

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/jbeegkljbamjjhemcgcijglmefnhjail/opgen_generated_files/bg.js
Line 982	const token = message.data.token;
Line 983	const refresh = message.data.refresh;
Line 987-988	chrome.storage.local.set({ jwtToken: token });
             chrome.storage.local.set({ refreshToken: refresh });
```

**Code:**

```javascript
// Content script (cs_1.js) - sendLoginMessage.js runs on https://app.dovirai.com/*
window.addEventListener('message', function (event) {
  if (event.source !== window) return;
  if (event.data.type && event.data.type === 'loginSuccess') {
    sendDataToBackground(event.data.payload);  // ← attacker-controlled via postMessage
  }
}, false);

function sendDataToBackground(data) {
  chrome.runtime.sendMessage({ type: 'loginSuccess', data: data });
}

// Background script (bg.js)
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'loginSuccess') {
    handleLoginSuccess(message, sendResponse);
  }
});

function handleLoginSuccess(message, sendResponse) {
  const token = message.data.token;  // ← attacker-controlled
  const refresh = message.data.refresh;  // ← attacker-controlled
  if (!token || !refresh) {
    throw new Error(`Token empty! ${message.data}`);
  }
  chrome.storage.local.set({ jwtToken: token }, () => {  // Storage write sink
    chrome.storage.local.set({ refreshToken: refresh }, () => {  // Storage write sink
      sendResponse({ status: 'success' });
    });
  });
}

// Later, tokens are retrieved and sent to hardcoded backend
const API_URL = 'https://api.dovirai.com';  // ← Hardcoded backend URL

const postJob = async (job) => {
    const { jwtToken } = await chrome.storage.local.get('jwtToken');

    let response = await fetch(`${API_URL}/jobs/`, {  // ← To hardcoded backend
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${jwtToken}`  // ← Poisoned token used here
        },
        body: JSON.stringify(job)
    });
    return response;
};
```

**Classification:** FALSE POSITIVE

**Reason:** While an attacker can poison the storage via postMessage (window.addEventListener on app.dovirai.com), the stored tokens are only sent to the hardcoded developer backend (https://api.dovirai.com). Per the methodology, data flowing to hardcoded backend URLs is trusted infrastructure and not exploitable. The attacker can poison the tokens, but they only impact communication with the developer's own backend server - compromising the developer's infrastructure is a separate issue from extension vulnerabilities. The poisoned data is not retrievable by the attacker through sendResponse, postMessage, or any attacker-controlled URL.
