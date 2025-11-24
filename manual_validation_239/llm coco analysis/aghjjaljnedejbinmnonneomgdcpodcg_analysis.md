# CoCo Analysis: aghjjaljnedejbinmnonneomgdcpodcg

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_chrome_runtime_MessageExternal → fetch_resource_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/aghjjaljnedejbinmnonneomgdcpodcg/opgen_generated_files/bg.js
Line 968	fetch(`${o}/user/contact/search?linkedin_url=${o$1}`, {credentials:"include"})

**Code:**

```javascript
// Background script (bg.js) - Line 968
// Import from constants file:
// const o = "https://api.jobmonk.ai";

chrome.runtime.onMessageExternal.addListener(async function(t, i, c) {
  // ... other actions ...

  if ("isContactSaved" === t.action) {
    const o$1 = t.linkedin_url;  // ← attacker-controlled
    fetch(`${o}/user/contact/search?linkedin_url=${o$1}`, {  // ← fetch to hardcoded backend
      credentials: "include"
    }).then((e => e.json())).then((e => {
      200 === e.code ? c({success: !0, contactInfo: e.result}) : c({success: !1});
    })).catch((e => {
      console.error("Error:", e), c({success: !1});
    }));
  }
});

// From chunks/constants-c61eaae7.js:
// const o = "https://api.jobmonk.ai"
```

**Classification:** FALSE POSITIVE

**Reason:** While the extension has `externally_connectable: {"matches": ["<all_urls>"]}` which allows any website to send external messages, and the attacker can control the `linkedin_url` parameter, the fetch request is made to a hardcoded backend URL (`https://api.jobmonk.ai`). The attacker is only controlling query parameters sent TO the developer's own backend server. According to the methodology, data sent to hardcoded backend URLs is considered trusted infrastructure, and compromising the developer's infrastructure is separate from extension vulnerabilities. This is classified as FALSE POSITIVE.
