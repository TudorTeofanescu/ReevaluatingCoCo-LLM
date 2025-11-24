# CoCo Analysis: bcnlhjaciolpiajnaeankcpdjabpeflh

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 3 (2 chrome_storage_local_set_sink, 1 fetch_resource_sink)

---

## Sink: fetch_source → Multiple Sinks

**CoCo Trace:**
```
from fetch_source to chrome_storage_local_set_sink (2 instances)
from fetch_source to fetch_resource_sink (1 instance)
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bcnlhjaciolpiajnaeankcpdjabpeflh/opgen_generated_files/bg.js
```

**Code:**

```javascript
// Background script - Variables with hardcoded URLs
var cx = "980c881780827100e";
var base_url_template = "https://cse.google.com/cse/element/v1?rsz=filtered_cse&num=50&hl=en&cx={cx}&cse_tok={cse_tok}&exp=csqr,cc&callback=google.search.cse.api";
var base_url = "";

// Search function using hardcoded Google CSE URL
function search_google() {
    let search_url = base_url + `&q=${query}`;
    console.log('1');
    ajax(search_url, google_callback); // ← Fetch from Google CSE
}

// Callback processes data FROM Google CSE API
function google_callback(data) {
    console.log('3');
    let key = 'tab' + tab_id;
    try {
        data = JSON.parse(data.replace("/*O_o*/", "").replace(/.*\(/, "").replace(/\)\;/, ""));
    } catch(e) {
        console.log('egnore');
    }
    // ... processing data from Google CSE ...

    darkob_search(function (result) {
        // ... merge results from Google and darkob ...

        chrome.storage.local.set({ [key]: data }, function () { // ← Store data from backends
            chrome.runtime.sendMessage({ done: true, tab_id: tab_id });
            chrome.browserAction.setBadgeText({ text: count + "", tabId: tab_id });
        });
    });
}

// Fetch from hardcoded darkob.co.ir backend
function darkob_search(callback) {
    fetch("https://darkob.co.ir/api/search-ext/" + original_query) // ← Hardcoded backend URL
        .then((response) => response.json())
        .then((json) => callback(json)); // ← Data FROM backend
}

// Ajax helper using fetch
function ajax(url, callback) {
    console.log('22');
    let options = {
        mode: 'cors',
        credentials: 'include',
        redirect: 'follow',
        cache: 'no-store'
    };
    fetch(url, options).then((response) => response.text())
        .then((text) => callback(text)); // ← Data FROM Google CSE
}

// Refresh token from hardcoded Google CSE
function refresh_token(callback) {
    ajax("https://cse.google.com/cse.js?cx=" + cx, function (data) { // ← Hardcoded URL
        let match = data.match(/\"cse_token\"\: \"(.*)\"/g)[0];
        let token = match.split(": ")[1].replace(/\"/g, "");
        base_url = base_url_template.replace("{cx}", cx).replace("{cse_tok}", token) + Math.floor(Math.random() * 1000);
        console.log(base_url);

        chrome.storage.local.set({ base_url: base_url }, callback); // ← Store data from backend
    });
}
```

**Classification:** FALSE POSITIVE

**Reason:** Data flows FROM hardcoded backend URLs, not from attacker. The extension fetches search results from two hardcoded backend services: Google Custom Search Engine (https://cse.google.com) and the extension's own backend (https://darkob.co.ir). The fetch() responses from these trusted backend servers are then stored in chrome.storage or used in subsequent fetch() requests. Per the methodology, data TO/FROM developer's hardcoded backend URLs is considered trusted infrastructure. The source is NOT attacker-controlled - it comes from responses from these hardcoded backend services. No external attacker can inject data into this flow unless they compromise Google's or darkob.co.ir's infrastructure, which is outside the scope of extension vulnerabilities.
