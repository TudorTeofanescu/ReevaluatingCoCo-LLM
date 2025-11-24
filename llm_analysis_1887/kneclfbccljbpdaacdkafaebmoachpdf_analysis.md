# CoCo Analysis: kneclfbccljbpdaacdkafaebmoachpdf

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 2 (both XMLHttpRequest_post_sink)

---

## Sink 1: bg_chrome_runtime_MessageExternal → XMLHttpRequest_post_sink (request.pass)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/kneclfbccljbpdaacdkafaebmoachpdf/opgen_generated_files/bg.js
Line 974: `'password': request.pass`

**Code:**

```javascript
// Background script (bg.js) - Lines 965-1001
chrome.runtime.onMessageExternal.addListener(
  function(request, sender, sendResponse) {
    const url = "https://api.airbnb.com/v1/authorize/"  // ← hardcoded backend URL
    const body = {
      'currency': 'USD',
      'locale': 'en-US',
      'username': request.uname,  // ← attacker-controlled
      'grant_type': 'password',
      'client_id': "3092nxybyb0otqw18e8nh5nty",
      'password': request.pass  // ← attacker-controlled
    }
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.open("POST", url, true);  // ← sends to hardcoded Airbnb API
    xmlhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xmlhttp.send(JSON.stringify(body))  // ← sink
    return true
  }
)
```

**Classification:** FALSE POSITIVE

**Reason:** This is attacker-controlled data being sent TO a hardcoded backend URL (https://api.airbnb.com/v1/authorize/). This is the extension's trusted infrastructure. The attacker can only send credentials to Airbnb's API, which is not a vulnerability in the extension - it's the intended functionality. The extension acts as a proxy to Airbnb's authentication service. Sending data to hardcoded developer/trusted backend URLs is explicitly classified as FALSE POSITIVE per the methodology.

---

## Sink 2: bg_chrome_runtime_MessageExternal → XMLHttpRequest_post_sink (request.uname)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/kneclfbccljbpdaacdkafaebmoachpdf/opgen_generated_files/bg.js
Line 971: `'username': request.uname`

**Code:**

```javascript
// Same code path as Sink 1
chrome.runtime.onMessageExternal.addListener(
  function(request, sender, sendResponse) {
    const url = "https://api.airbnb.com/v1/authorize/"  // ← hardcoded backend URL
    const body = {
      'username': request.uname,  // ← attacker-controlled
      'password': request.pass
    }
    xmlhttp.send(JSON.stringify(body))  // ← sends to hardcoded Airbnb API
  }
)
```

**Classification:** FALSE POSITIVE

**Reason:** Same as Sink 1 - attacker-controlled data flows TO hardcoded trusted infrastructure (Airbnb API). This is the intended functionality where the extension proxies authentication requests to Airbnb. Not a vulnerability per the methodology's hardcoded backend URL rule.
