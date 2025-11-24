# CoCo Analysis: cdnfbnpopdaplbhjnepdaklmciknnnom

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: jQuery_post_source → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/cdnfbnpopdaplbhjnepdaklmciknnnom/opgen_generated_files/bg.js
Line 310: var responseText = 'data_from_url_by_post'; (CoCo framework code)
Line 1042: var ret = JSON.parse(data);
Line 1050: s.sync.set({ user_id: ret.user_id }, function () { });

**Code:**

```javascript
// Background script (background/script.js) - lines 967, 1038-1062
var api_server = "https://moreaboutme.herokuapp.com/" // ← Hardcoded backend URL

// ... later in chrome.tabs.onUpdated listener
if (changeInfo.status == 'loading' &&
    changeInfo.url.startsWith("https://www.facebook.com/connect/login_success.html#access_token=")) {
    access_token = getParameterByName('access_token', changeInfo.url);
    console.log(access_token);

    // POST to hardcoded backend
    $.post(api_server + "verify_user", { token: access_token }, function (data) {
        var ret = JSON.parse(data); // Data FROM hardcoded backend

        // show success or error page
        if (ret.ok == '1') {
            var s;
            if (chrome) { s = chrome.storage; }
            else { s = storage; }
            s.sync.set({ token: access_token }, function () { });
            s.sync.set({ user_id: ret.user_id }, function () { }); // ← Store backend response
            var t;
            if (chrome) { t = chrome.tabs; }
            else { t = tabs; }
            t.remove(tab.id, function () { });
        }
        else {
            var ttt;
            if (chrome) { ttt = chrome.tabs; }
            else { ttt = tabs; }
            ttt.update(tab.id, { url: "https://www.moreaboutme.com/error.html" });
        }
    });
}
```

**Classification:** FALSE POSITIVE

**Reason:** Hardcoded backend URL (trusted infrastructure). The flow is data FROM the developer's hardcoded backend (https://moreaboutme.herokuapp.com/) to chrome.storage.sync.set. The extension POSTs a Facebook access token to its own backend for verification, receives a response containing user_id, and stores that response data in storage. According to the methodology, data FROM hardcoded developer backend URLs is considered trusted infrastructure, not an attacker-controlled source. The developer trusts their own backend server, and compromising the backend infrastructure is a separate issue from extension vulnerabilities. There is no external attacker trigger or attacker-controlled data flowing to the storage.
