# CoCo Analysis: aoliopcinjofnjpckiknoomodchkjolk

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 15 (all variants of same flow)

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/aoliopcinjofnjpckiknoomodchkjolk/opgen_generated_files/bg.js
Line 1233-1247: Multiple console.log statements logging request properties
Line 1268-1274: chrome.storage.sync.set with multiple request properties

**Code:**

```javascript
// Background script (bg.js) - Line 1230
chrome.runtime.onMessageExternal.addListener(
	function(request, sender, sendResponse) { // ← External message handler
		console.log("Recieving Message from Web Site!");
		console.log("imageleft: " + request.imageleft); // ← attacker-controlled
		console.log("imagetop: " + request.imagetop);
		console.log("imageheight: " + request.imageheight);
		console.log("imagewidth: " + request.imagewidth);
		console.log("documentWindowX: " + request.documentWindowX);
		console.log("documentWindowY: " + request.documentWindowY);
		console.log("imageWindowX: " + request.imageWindowX);
		console.log("imageWindowY: " + request.imageWindowY);
		console.log("documentleft: " + request.documentleft);
		console.log("documenttop: " + request.documenttop);
		console.log("documentheight: " + request.documentheight);
		console.log("documentwidth: " + request.documentwidth);
		console.log("queueWindowX: " + request.queueWindowX);
		console.log("queueWindowY: " + request.queueWindowY);
		console.log("queueleft: " + request.queueleft);

		var details = ['imageleft', 'imagetop','imagewidth', 'imageheight',
			'documentleft', 'documenttop','documentwidth', 'documentheight',
			'documentWindowX', 'documentWindowY', 'imageWindowX', 'imageWindowY',
			'queueWindowX', 'queueWindowY', 'queueleft', 'messageNumber'];

		chrome.storage.sync.get(details, function(getObj) {
			var messageNumber;
			if (getObj.messageNumber == null) {
				messageNumber = 0;
			} else {
				messageNumber = Number(getObj.messageNumber);
			}
			messageNumber = messageNumber + 1;

			chrome.storage.sync.set({
				imageleft: request.imageleft, // ← attacker-controlled data
				imagetop: request.imagetop,
				imagewidth: request.imagewidth,
				imageheight: request.imageheight,
				documentleft: request.documentleft,
				documenttop: request.documenttop,
				documentwidth: request.documentwidth,
				documentheight: request.documentheight,
				documentWindowX: request.documentWindowX,
				documentWindowY: request.documentWindowY,
				imageWindowX: request.imageWindowX,
				imageWindowY: request.imageWindowY,
				queueWindowX: request.queueWindowX,
				queueWindowY: request.queueWindowY,
				queueleft: request.queueleft,
				messageNumber: messageNumber,
				// Also saves old values
				oldImageLeft: getObj.imageleft,
				oldImageTop: getObj.imagetop
				// ... etc
			}, function() {
				console.log("Storage Complete");
			});
		});
	}
);
```

**Classification:** FALSE POSITIVE

**Reason:** Although the extension has chrome.runtime.onMessageExternal listener that accepts messages from externally_connectable domains (http://dev-app5:9082/*, https://veritiv-test2.miria-active.net:9443/*, https://veritiv.miria-active.net:9443/*), and per the methodology we ignore manifest.json restrictions, this is still incomplete storage exploitation. The attacker can poison storage with arbitrary layout/position values, but there is no mechanism to retrieve these values back. The stored data is never sent via sendResponse, postMessage, or used in any operation that would allow the attacker to observe or retrieve the poisoned values. Storage poisoning alone without a retrieval path is NOT exploitable per the methodology.
