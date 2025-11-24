# CoCo Analysis: jgmlagepgchaedmnjdabilicbjoleknd

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 16 (multiple traces through same code path)

---

## Sink: fetch_source → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/jgmlagepgchaedmnjdabilicbjoleknd/opgen_generated_files/bg.js
Line 265 - fetch source (CoCo framework)
Line 1683 - text.split(/\n/)
Line 1691-1698 - line parsing and processing
Storage sink at line 1457 in cfg.save()

**Code:**

```javascript
// Background script - Lines 1664-1723 in bg.js
var g_start_page = "";

// Get current tab URL
chrome.tabs.query({currentWindow: true, active: true}, function(tabs){
	if(str_is_empty(g_start_page) && tabs[0] != null){
		g_start_page = tabs[0].url; // ← URL from current tab
		parse_start_page();
	}
});

function parse_start_page(){
	if(str_is_empty(g_start_page) || !str_starts_with(g_start_page, "http")){
		log.error("update_policy, Invalid start page!");
		return;
	}

	var tgt_url = g_start_page;
	if(tgt_url.indexOf("?") == -1){
		tgt_url += "?" + unix_timestamp();
	}

	fetch(tgt_url) // ← fetch from user's current tab URL
	.then(function(response){
		return response.text();
	})
	.then(function(text){
		var lines = text.split(/\n/);
		for(var i = 0; i < lines.length; i++){
			var line = lines[i];
			if(line.indexOf("<body") > -1 || line.indexOf("<BODY") > -1){
				break;
			}

			// Parse meta tag with cxblock
			if(line.indexOf("<meta") > -1 && line.indexOf("cxblock") > -1){
				line = line.replace(/^.+content/, "");
				line = line.replace(/\s+/g, "");
				line = line.replace(/[='"\/>]/g, "");

				var arr = line.split(/:/);
				if(arr.length < 2){
					return;
				}

				var server = arr[0]; // ← attacker-controlled (from meta tag)
				var token = arr[1];  // ← attacker-controlled (from meta tag)

				if(str_is_empty(server) || server.indexOf("/") > -1 || !is_valid_ip(server)){
					return;
				}

				// Save to storage
				cfg.save(server, token); // ← stores to chrome.storage.sync.set
				cfg.load();
				return;
			}
		}
	})
	.catch(function() {
		log.error("update_policy, Connection error!");
	});
}

// Config save function - Line 1455
this.save = function(server, token){
	var items = {server: server, token: token};
	chrome.storage.sync.set(items, function(){ // ← storage sink
		log.info("Config.save, New option saved.");
	});
	// Data is NOT sent back to attacker
};
```

**Classification:** FALSE POSITIVE

**Reason:** This is incomplete storage exploitation (storage poisoning without retrieval). The flow is:
1. Extension fetches the user's current tab URL
2. Parses HTML response for meta tag with "cxblock" content
3. Extracts server IP and token from meta tag content
4. Stores them to chrome.storage.sync.set

While an attacker controlling a webpage could inject a meta tag like `<meta name="cxblock" content="192.168.1.1:malicious_token">`, the stored values are never retrieved and sent back to the attacker. Per the methodology: "Storage poisoning alone is NOT a vulnerability" - the attacker must be able to retrieve the poisoned data via sendResponse, postMessage, or other accessible output. No such retrieval path exists in this code.

Note: All 16 detected sinks are variations of the same flow with different intermediate line numbers (lines 1691-1698 with different regex replace operations), but they all lead to the same cfg.save() storage sink.
