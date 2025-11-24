# CoCo Analysis: adpcpmhlpjfhgjlgjgcdbignknkfochd

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 2 (chrome_storage_sync_clear_sink, chrome_storage_sync_set_sink)

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/adpcpmhlpjfhgjlgjgcdbignknkfochd/opgen_generated_files/bg.js
Line 971	chrome.runtime.onMessageExternal.addListener((a,b,c)=>{if(b.origin===$jscompDefaultExport$$module$js$links.getFrontendURL()&&(b={login:()=>{storeUserPrefs$$module$js$bg_storage(a.auth)},logout:()=>{clearUserPrefs$$module$js$bg_storage()},test:()=>{getUserPrefs$$module$js$bg_storage().then(d=>{console.log(d)})},reqGet:()=>{fetchRequestID$$module$js$bg_server().then(d=>{console.log("fetch req:",d)})},reqCheck:()=>{getRequest$$module$js$bg_storage().then(d=>{console.log("check req:",d)})},reqUpdateCtxMenu:()=>
Line 965	function storeUserPrefs$$module$js$bg_storage(a){chrome.storage.sync.set({token:a},function(){})}

**Code:**

```javascript
// Line 965 - Storage function that stores user token
function storeUserPrefs$$module$js$bg_storage(a){
  chrome.storage.sync.set({token:a},function(){})
}

// Line 971 - onMessageExternal listener with origin check
chrome.runtime.onMessageExternal.addListener((a,b,c)=>{
  // Origin validation checks if sender is from the extension's frontend
  if(b.origin===$jscompDefaultExport$$module$js$links.getFrontendURL() && ...) {
    b={
      login:()=>{storeUserPrefs$$module$js$bg_storage(a.auth)}, // ← Stores a.auth
      logout:()=>{clearUserPrefs$$module$js$bg_storage()},
      test:()=>{getUserPrefs$$module$js$bg_storage().then(d=>{console.log(d)})},
      reqGet:()=>{fetchRequestID$$module$js$bg_server().then(d=>{console.log("fetch req:",d)})},
      reqCheck:()=>{getRequest$$module$js$bg_storage().then(d=>{console.log("check req:",d)})},
      reqUpdateCtxMenu:()=>{...}
    };
    if(b[a.cmd]) b[a.cmd]();
    c({received:!0});
  }
});

// Line 967 - Frontend URL configuration (hardcoded trusted infrastructure)
var $jscompDefaultExport$$module$js$links={
  getFrontendURL:()=>"dev"===mode$$module$js$links?
    devFrontend$$module$js$links:prodFrontend$$module$js$links,
  ...
}
// devFrontend = "http://localhost:5173"
// prodFrontend = "https://scribe.powerext.co"
```

**Classification:** FALSE POSITIVE

**Reason:** This is storage poisoning that writes to hardcoded trusted infrastructure. The extension validates that external messages come from b.origin === getFrontendURL() which returns the developer's own frontend domain ("https://scribe.powerext.co" in production or "http://localhost:5173" in dev mode). While the methodology states to ignore manifest.json externally_connectable restrictions, the code itself performs origin validation against hardcoded developer-controlled domains. The data flow is: developer's frontend → chrome.storage.sync.set({token: value}). This is attacker sending data TO the extension's trusted backend/frontend ecosystem, which falls under the "Hardcoded backend URLs remain trusted infrastructure" rule. There's no retrieval path showing the stored token flows back to an external attacker. This is an internal authentication flow between trusted components of the same application.

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_sync_clear_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/adpcpmhlpjfhgjlgjgcdbignknkfochd/opgen_generated_files/bg.js
Line 971	chrome.runtime.onMessageExternal.addListener((a,b,c)=>{if(b.origin===$jscompDefaultExport$$module$js$links.getFrontendURL()&&(b={login:()=>{storeUserPrefs$$module$js$bg_storage(a.auth)},logout:()=>{clearUserPrefs$$module$js$bg_storage()},test:()=>{getUserPrefs$$module$js$bg_storage().then(d=>{console.log(d)})},reqGet:()=>{fetchRequestID$$module$js$bg_server().then(d=>{console.log("fetch req:",d)})},reqCheck:()=>{getRequest$$module$js$bg_storage().then(d=>{console.log("check req:",d)})},reqUpdateCtxMenu:()=>
Line 965	function clearUserPrefs$$module$js$bg_storage(){chrome.storage.sync.clear()}

**Code:**

```javascript
// Line 965 - Logout function clears all storage
function clearUserPrefs$$module$js$bg_storage(){
  chrome.storage.sync.clear()
}

// Line 971 - onMessageExternal listener allows logout command
chrome.runtime.onMessageExternal.addListener((a,b,c)=>{
  if(b.origin===$jscompDefaultExport$$module$js$links.getFrontendURL()) {
    b={
      logout:()=>{clearUserPrefs$$module$js$bg_storage()}, // ← Clears storage
      ...
    };
    if(b[a.cmd]) b[a.cmd]();
  }
});
```

**Classification:** FALSE POSITIVE

**Reason:** Same as above - this operation is only accessible from the developer's hardcoded trusted frontend domain. The logout functionality clearing storage is part of the normal authentication flow between trusted components. This is not an exploitable vulnerability as it requires messages to originate from the extension's own trusted infrastructure (scribe.powerext.co).
