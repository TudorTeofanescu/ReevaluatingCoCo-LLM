# CoCo Analysis: njmehopjdpcckochcggncklnlmikcbnb

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1 (referenced only CoCo framework code)

---

## Sink: bg_chrome_runtime_MessageExternal → fetch_resource_sink (referenced only CoCo framework code)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/njmehopjdpcckochcggncklnlmikcbnb/opgen_generated_files/bg.js
Line 965	(minified webpack bundle - entire extension code)

**Code:**

The extension code at line 965 is heavily minified webpack bundle. Examining the minified code reveals:

```javascript
// Module 24587 - Hardcoded backend URLs
const o="https://members.helium10.com"
const c=`${o}/api/v1`
const s=`${c}/customers/me`  // userInfoLink
const u=`${c}/customers/segment-track`  // iH - segment tracking
const d=`${c}/customers/me/chrome-extension`
const g=`${c}/site/get-parser-config`

// Module 49430 - Check alerts
const i=e=>{
  // ...
  const t=yield fetch((0,r.kK)(n));  // ← Fetch to hardcoded backend
  // ...
}

// Module 97610 - Segment event tracking
const d=e=>{
  // ...
  return fetch(r.iH,{  // ← Fetch to hardcoded backend segment URL
    method:"POST",
    headers:{Accept:"application/json","Content-Type":"application/json"},
    body:JSON.stringify({name:e.name,properties:u({...})})
  })
}

// Module 10194 - User info fetch
const e=yield(0,o.updateLinkWithAccountId)(o.userInfoLink);
return fetch(e,{}).then(...)  // ← Fetch to hardcoded backend
```

**Classification:** FALSE POSITIVE

**Reason:** All fetch operations in the minified code go to hardcoded backend URLs (members.helium10.com, members.h10.com.cn). These are trusted infrastructure under the developer's control. Data flows TO hardcoded backends for legitimate functionality (user info, segment tracking, alerts). Compromising developer infrastructure is separate from extension vulnerabilities.
