# CoCo Analysis: cmlkmalcjcbmledhdedbljhfejciicbh

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 10 (many duplicates of same flows)

---

## Sink 1-8: bg_chrome_runtime_MessageExternal → jQuery_ajax_settings_data_sink

**CoCo Trace:**
$FilePath$/cmlkmalcjcbmledhdedbljhfejciicbh/opgen_generated_files/bg.js
Line 1014: data: request.data

**Analysis:**

Multiple flows detected from external messages to AJAX data sinks. All flows send attacker-controlled data to hardcoded backend URLs owned by the extension developer.

**Code:**

```javascript
// Background script - External message handler
chrome.runtime.onMessageExternal.addListener(
  function (request, sender, sendResponse) {
    if (request.type === 'FetchPlayerPrices') {
      const url = 'https://apisf.futalert.co.uk/api/Player/FetchPlayerPrices'; // ← Hardcoded backend
      $.ajax({
        url: url,
        method: 'POST',
        type: 'json',
        data: request.data, // ← attacker-controlled data
        success: function (res) {
          sendResponse({ success: true, res: res });
        }
      });
    } else if (request.type === 'PushPrices') {
      const url = 'https://apisf.futalert.co.uk/api/Player/PushPricesFUTAlert'; // ← Hardcoded backend
      request.data.Source = 'FUTAlert';
      request.data.Version = manifest && manifest.version ? manifest.version : '1.0.9';
      $.ajax({
        url: url,
        method: 'POST',
        type: 'json',
        data: request.data, // ← attacker-controlled data
        success: function (res) {
          sendResponse({ success: true, res: res });
        }
      });
    } else if (request.type === 'GetActiveAds') {
      const url = 'https://apisf.futalert.co.uk/api/user/getactiveads'; // ← Hardcoded backend
      $.ajax({
        url: url,
        method: 'POST',
        type: 'json',
        data: request.data, // ← attacker-controlled data
      });
    }
  });
```

**Classification:** FALSE POSITIVE

**Reason:** All data flows go TO hardcoded backend URLs (apisf.futalert.co.uk). This is trusted infrastructure owned by the extension developer. Sending attacker-controlled data to the developer's own backend is not a vulnerability - the backend is expected to validate and handle untrusted input.

---

## Sink 9: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/cmlkmalcjcbmledhdedbljhfejciicbh/opgen_generated_files/bg.js
Line 1045: data[request.key] = JSON.parse(request.data)

**Code:**

```javascript
chrome.runtime.onMessageExternal.addListener(
  function (request, sender, sendResponse) {
    if (request.type === 'SetStorage') {
      const data = {};
      data[request.key] = JSON.parse(request.data); // ← attacker-controlled
      chrome.storage.local.set(data, function (res) {
        sendResponse(data);
      });
    }
  });
```

**Classification:** FALSE POSITIVE

**Reason:** While this allows external entities to write to storage via chrome.runtime.onMessageExternal, there is no complete exploitation chain. The extension has `externally_connectable` configured to only allow connections from specific domains (easports.com, ea.com, apisf.futalert.co.uk). The storage write alone without a retrieval path to attacker-accessible output does not constitute a complete vulnerability. Additionally, examining line 1037 shows GetStorage retrieves data but only sends it back to the requester via sendResponse, which would only go to the allowed domains configured in externally_connectable, not to an arbitrary attacker.

---

## Sink 10: storage_local_get_source → sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/cmlkmalcjcbmledhdedbljhfejciicbh/opgen_generated_files/bg.js
Line 687: var storage_local_get_source = {'key':'value'} (CoCo framework code only)

**Classification:** FALSE POSITIVE

**Reason:** CoCo only referenced framework mock code at line 687, not actual extension code. While the extension does have a GetStorage handler at line 1037 that reads from storage and sends via sendResponse, this only responds to entities in the externally_connectable allowlist (specific trusted domains). This is not attacker-accessible information disclosure.
