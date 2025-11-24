# CoCo Analysis: pfkcallckpiapbmignokbdjamkejnimk

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: cs_window_eventListener_message → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/pfkcallckpiapbmignokbdjamkejnimk/opgen_generated_files/cs_0.js
Line 470	window.addEventListener('message', function(event) {
	event
Line 472	        cetak_label_alamat_token: event.data.access_token
	event.data
Line 472	        cetak_label_alamat_token: event.data.access_token
	event.data.access_token

**Code:**

```javascript
// Content script - Entry point (auth.js)
window.addEventListener('message', function(event) {
    chrome.storage.local.set({
        cetak_label_alamat_token: event.data.access_token // ← attacker-controlled data to storage
    })
});

// Popup script - Reads token but no exploitable output (popup.js)
function isLoggedIn(){
    return chrome.storage.local.get(['cetak_label_alamat_token'], function(result){
        if(typeof result.cetak_label_alamat_token == 'undefined'){
            document.getElementById('extension_item_id').value = chrome.runtime.id;
        }
        else{
            var content = document.querySelectorAll('body');
            content = content[0];
            content.innerHTML = 'Printing';
            content.style.minHeight = '10px';
            content.style.minWidth = '10px';
            chrome.tabs.executeScript(tabs[0].id, {
                file : "main.js" // ← Executes printing script (no attacker benefit)
            }, function(){
                console.log('done 1');
            })
        }
    });
}
```

**Classification:** FALSE POSITIVE

**Reason:** This is storage poisoning without a complete exploitation chain. While the token is stored from window.postMessage and later retrieved in popup.js, it's only used to determine whether to display the extension ID or execute a printing script (main.js). The token value is never sent back to the attacker via sendResponse/postMessage, nor is it used in fetch requests or other operations where the attacker could benefit. The main.js script only performs local DOM printing operations with no privileged API calls using the token.
