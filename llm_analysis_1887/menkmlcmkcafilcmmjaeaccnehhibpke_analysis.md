# CoCo Analysis: menkmlcmkcafilcmmjaeaccnehhibpke

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1 (chrome_storage_local_set_sink)

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/menkmlcmkcafilcmmjaeaccnehhibpke/opgen_generated_files/bg.js
Line 1195: chrome.storage.local.set({ "clp_current_user":msg.user }).then(() => {
Line 1199: chrome.storage.local.set({ "clp_user_email":msg.user_email }).then(() => {

**Code:**

```javascript
// Background script - External message handler (bg.js line 1186)
chrome.runtime.onMessageExternal.addListener(function(msg, sender) {
    console.log("requesting url", sender.url, "url is allowed?:", sender.url.indexOf("classifii") != -1);

    if (sender.url.indexOf("classifii") != -1) { // ← URL validation check
        /* OK, this page is allowed to communicate with me */
        if (msg.status === "logged_in") {
            /* Cool, the user is logged in */
            chrome.storage.local.set({ "clp_logged_in":"true" }).then(() => {
                console.log("set clp_logged_in to true");
            });
            chrome.storage.local.set({ "clp_current_user":msg.user }).then(() => { // ← storage write
                console.log("set clp_logged_user to", msg.user);
                currentUser.user_id = msg.user;
            });
            chrome.storage.local.set({ "clp_user_email":msg.user_email }).then(() => { // ← storage write
                console.log("set clp_user_email to", msg.user_email);
                currentUser.user_email = msg.user_email;
            });
        } else if (msg.status === "logged_out") {
            /* How sad, the user is leaving */
            chrome.storage.local.set({ "clp_logged_in":"false" }).then(() => {
                console.log("set clp_logged_in to false");
            });
        }
    }
});

// Later used in background (bg.js lines 1098, 1121, etc.)
function addItem(title, price) {
    var data = {
        "added_user_id": currentUser.user_id, // ← uses stored user_id
        // ... sent to hardcoded backend classifii.com
    };
    const url = ps_item_entry_url; // = "https://www.classifii.com/wp/cl_app/ps_item_entry.php"
    postJSON(url, data).then(addItemSuccess, addItemError);
}

function get_fc_list() {
    var data = {"user_id": currentUser.user_id}; // ← uses stored user_id
    const url = cl_base_url + "get_fc_list.php"; // = "https://www.classifii.com/wp/cl_app/get_fc_list.php"
    postJSON(url, data).then(get_fc_list_Success, get_fc_list_Error);
}
```

**Classification:** FALSE POSITIVE

**Reason:** This is storage poisoning combined with data sent to hardcoded backend URL (trusted infrastructure). The flow is:

1. External message from classifii.com domains → writes msg.user and msg.user_email to storage
2. Extension later reads currentUser.user_id and sends it to hardcoded backend (https://www.classifii.com/wp/cl_app/...)

Per the methodology, "Data TO hardcoded backend: attacker-data → fetch('https://api.myextension.com')" is FALSE POSITIVE. The extension sends the poisoned user_id to the developer's own trusted infrastructure (classifii.com backend), not to an attacker-controlled destination. While an attacker controlling classifii.com domains could poison the storage, the poisoned data only flows to the same trusted backend - there's no exploitation path where the attacker retrieves the data back or uses it in a privileged operation. The manifest.json allows externally_connectable only to classifii.com domains, which are the developer's own infrastructure.

Additionally, there's no complete storage exploitation chain. The stored values don't flow back to the attacker via sendResponse/postMessage, nor are they used in executeScript/eval. They're only sent to the hardcoded backend URLs, which is the developer's trusted infrastructure. Compromising the developer's own website is an infrastructure issue, not an extension vulnerability.
