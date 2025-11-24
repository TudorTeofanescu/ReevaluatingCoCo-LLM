# CoCo Analysis: aomogjppckmpnifdagcejoaaalibinok

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/aomogjppckmpnifdagcejoaaalibinok/opgen_generated_files/bg.js
Line 965: Minimized JavaScript code containing chrome.runtime.onMessageExternal.addListener

**Code:**

```javascript
// Background script (bg.js) - chrome.runtime.onMessageExternal.addListener
chrome.runtime.onMessageExternal.addListener((t,e,n)=>{
	console.log(t);
	let r={xpAdminId:t.data.xpAdminId,xpAdminName:t.data.xpAdminName}, // ← attacker-controlled
	    o=t.data.token; // ← attacker-controlled

	// Store attacker-controlled data
	return chrome.storage.sync.set({userMessage:r,token:o}), // Storage sink
	       n("已收到用户信息"), // Send back hardcoded string, not stored data
	       chrome.storage.sync.get("pageId",({pageId:t})=>{
		       t&&(chrome.tabs.sendMessage(t,{sign:"lwGetData"}),
		       chrome.storage.sync.set({pageId:null}))
	       }),
	       !0
});
```

**Classification:** FALSE POSITIVE

**Reason:** Although the extension has chrome.runtime.onMessageExternal listener that accepts messages from externally_connectable domains (`*://*.lwhs.me/*`), and per the methodology we ignore manifest.json restrictions, this is incomplete storage exploitation. The attacker from lwhs.me can poison storage with arbitrary xpAdminId, xpAdminName, and token values, but the sendResponse callback only returns a hardcoded confirmation string ("已收到用户信息" which means "User information received") - not the stored data itself. There is no mechanism for the attacker to retrieve the poisoned storage values back through sendResponse, postMessage, or any other attacker-accessible output. Storage poisoning alone without a retrieval path is NOT exploitable per the methodology.
