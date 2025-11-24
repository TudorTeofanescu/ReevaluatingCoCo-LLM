# CoCo Analysis: daobbpakjlelcbbmapgfligpgbadgnae

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/daobbpakjlelcbbmapgfligpgbadgnae/opgen_generated_files/bg.js
Line 965 (minified code containing onMessageExternal listener)

**Code:**

```javascript
// Background script (bg.js) - External message handler (reformatted from minified)
chrome.runtime.onMessageExternal.addListener((function(e, t) {
  if (t.url && (t.url.includes("localhost") || t.url.includes("edmigo.in")) && e) {
    if (e.type === "signIn" && e.session) {
      chrome.storage.local.set({edmigoSession: e.session}, () => {}); // Storage write
    } else if (e.type === "signOut") {
      chrome.storage.local.remove("edmigoSession");
    }
  }
}));

// Later usage - retrieving stored session for backend auth
function r() {
  return new Promise((e => {
    chrome.storage.local.get("edmigoSession", (function(t) {
      if (t.edmigoSession) {
        let s = JSON.parse(t.edmigoSession);
        // Extract access token for API calls
        e({
          userName: s?.user?.username,
          accessToken: s?.backend_tokens?.access_token
        });
      } else {
        e(void 0);
      }
    }));
  }));
}

// Used to make authenticated requests to developer's backend
const o = yield r();
const l = yield fetch("https://api.edmigo.in/api/v1/tutor", {
  method: "POST",
  headers: {
    accept: "application/json",
    Authorization: `Bearer ${o.accessToken}`,
    "Content-Type": "application/json"
  },
  body: JSON.stringify({...})
});
```

**Classification:** FALSE POSITIVE

**Reason:** While external messages can write to storage (storage poisoning), the stored session data is only retrieved and used to authenticate requests to the developer's hardcoded backend infrastructure (api.edmigo.in). The data does not flow back to the attacker or enable any exploitable impact. Per the methodology, "storage.get → fetch(hardcodedBackendURL)" is FALSE POSITIVE as it involves trusted infrastructure, and "Storage poisoning alone is NOT a vulnerability" without a retrieval path back to the attacker or exploitable usage.
