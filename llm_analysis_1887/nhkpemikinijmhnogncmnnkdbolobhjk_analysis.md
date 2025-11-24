# CoCo Analysis: nhkpemikinijmhnogncmnnkdbolobhjk

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/nhkpemikinijmhnogncmnnkdbolobhjk/opgen_generated_files/bg.js
Line 981			if (request.appId) {
	request.appId
```

**Code:**

```javascript
// Background script (line 969)
chrome.runtime.onMessageExternal.addListener(function(
	request,
	sender,
	sendResponse
) {
	let extensionTabs = [];
	if (request) {
		if (request.message) {
			if (request.message == "version") {
				sendResponse({ version: 1.0 });
			}
		}
		if (request.appId) {
			chrome.storage.local.set({ appId: request.appId }); // ← attacker-controlled
			chrome.storage.local.set({ appURL: sender.tab.url });
			chrome.storage.local.set({ tabId: extensionTabs });
		}
	}
});

// Storage is only read internally (line 990) - no retrieval path to attacker
chrome.tabs.onCreated.addListener(function(tab) {
	chrome.storage.local.get("tabId", function(data) {
		let extensionTabs = data.tabId || [];
		extensionTabs.push(tab.id);
		chrome.storage.local.set({ tabId: extensionTabs });
		// No sendResponse or postMessage back to attacker
	});
});
```

**Classification:** FALSE POSITIVE

**Reason:** Incomplete storage exploitation - attacker can trigger storage.set via chrome.runtime.onMessageExternal, but there is no retrieval path that returns the stored data back to the attacker via sendResponse, postMessage, or any other attacker-accessible output.
