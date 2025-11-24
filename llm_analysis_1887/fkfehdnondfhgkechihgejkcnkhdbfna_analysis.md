# CoCo Analysis: fkfehdnondfhgkechihgejkcnkhdbfna

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: fetch_source → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/fkfehdnondfhgkechihgejkcnkhdbfna/opgen_generated_files/bg.js
Line 265	var responseText = 'data_from_fetch';

**Code:**

```javascript
// Function to get team's root asset ID from Moqups API
function getUniqueId(teamId, callback){
	const opts = {method: 'GET'};
	fetch('https://api.moqups.com/api/v1/teams/' + teamId + '/rootAsset', opts)  // ← Hardcoded backend
	.then(function(response){
		return response.json();
	}).then(function(response){
		chrome.storage.local.set({"parentId": response.uniqueId}, () => {  // ← Store response from trusted API
			if(callback){
				callback({"done": true});
			}
		});
		return response;
	}).catch(function(error ){
		// Nullify Id
		chrome.storage.local.set({"parentId": null}, () => {});
	});
}

// Function to check if user is logged in via Moqups API
function isLoggedIn(callback){
	const opts = {method: 'GET'};
	fetch('https://api.moqups.com/api/v1/session', opts)  // ← Hardcoded backend
	.then(function(response){
		return response.json();
	})
	.then(function(response){
		// Set new Id and then callback
		// ... stores session info
	})
}

// Message handler (internal messages only, NOT onMessageExternal)
chrome.runtime.onMessage.addListener(
	function(request, sender, sendResponse){
		if(request.message === "get-team-id"){
			getUniqueId(request.teamId, function(resp){
				sendResponse(resp);
			});
		}
		// ... other internal message handlers
		return true;
	}
);
```

**Classification:** FALSE POSITIVE

**Reason:** The fetch calls are made to hardcoded trusted backend (api.moqups.com, listed in manifest permissions). The extension stores session and team information from the developer's own API. The message listener is chrome.runtime.onMessage (internal messages from extension's own content scripts), NOT onMessageExternal, so external websites cannot trigger this flow. This is trusted infrastructure, not attacker-controlled data.
