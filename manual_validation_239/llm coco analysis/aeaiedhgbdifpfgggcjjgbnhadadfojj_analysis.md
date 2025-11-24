# CoCo Analysis: aeaiedhgbdifpfgggcjjgbnhadadfojj

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1 (chrome_storage_local_set_sink)

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/aeaiedhgbdifpfgggcjjgbnhadadfojj/opgen_generated_files/bg.js
Line 968	chrome.runtime.onMessageExternal.addListener((t,i,e)=>{(t==null?void 0:t.name)==="chief_ask_has_install"?e(!0):(t==null?void 0:t.name)==="chief_chrome_login_success"?(chrome.storage.local.set({chief_persist_token:t==null?void 0:t.val},()=>{}),e(!0)):(t==null?void 0:t.name)==="chief_to_jump"?(chrome.tabs.create({url:t==null?void 0:t.url}),e(!0)):(t==null?void 0:t.name)==="chief_close"?(chrome.tabs.query({active:!0,currentWindow:!0},r=>{r.length>0&&chrome.tabs.sendMessage(r[0].id,{closeVisible:!0});}),e(!0)):t==="chief_ask_in_chrome"&&e(!0);});

**Code:**

```javascript
// Line 968 - onMessageExternal listener with multiple command handlers
chrome.runtime.onMessageExternal.addListener((t,i,e)=>{
  // Command: chief_ask_has_install - responds with true
  (t==null?void 0:t.name)==="chief_ask_has_install"?e(!0):

  // Command: chief_chrome_login_success - stores token
  (t==null?void 0:t.name)==="chief_chrome_login_success"?
    (chrome.storage.local.set({chief_persist_token:t==null?void 0:t.val},()=>{}),e(!0)): // ← Stores t.val

  // Command: chief_to_jump - opens new tab with URL
  (t==null?void 0:t.name)==="chief_to_jump"?
    (chrome.tabs.create({url:t==null?void 0:t.url}),e(!0)):

  // Command: chief_close - sends message to close
  (t==null?void 0:t.name)==="chief_close"?
    (chrome.tabs.query({active:!0,currentWindow:!0},r=>{
      r.length>0&&chrome.tabs.sendMessage(r[0].id,{closeVisible:!0});
    }),e(!0)):

  // Command: chief_ask_in_chrome - responds with true
  t==="chief_ask_in_chrome"&&e(!0);
});
```

**Manifest.json externally_connectable:**
```json
"externally_connectable": {
  "matches": [
    "https://common.app.sxrjg.com/chrome",
    "https://naisaas_dev.app.sxrjg.com/login",
    "*://*.app.sxrjg.com/*",
    "*://*.sandbox.sxrjg.com/*",
    "*://*.sxrjg.com/*",
    "*://*.app.jidele.com/*",
    "*://*.sandbox.jidele.com/*",
    "*://*.jidele.com/*"
  ]
}
```

**Classification:** FALSE POSITIVE

**Reason:** This is storage poisoning that writes data TO hardcoded developer-controlled domains. The manifest.json shows externally_connectable is restricted to the developer's own domains (*.sxrjg.com and *.jidele.com). While the methodology says to ignore manifest restrictions, the critical analysis rules state: "Hardcoded backend URLs remain trusted infrastructure" and "Data TO/FROM developer's own backend servers = FALSE POSITIVE". The whitelisted domains (sxrjg.com, jidele.com) are the developer's own infrastructure based on the extension name ("记得了" / Context Note) and the domain patterns showing app/sandbox subdomains. This is an authentication flow where the developer's website communicates with their own extension to store login tokens. There is no retrieval path showing the stored token flows back to any attacker-accessible output. This is storage.set only without a storage.get → attacker path, making it incomplete storage exploitation per the methodology.
