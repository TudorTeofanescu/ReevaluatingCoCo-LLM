# CoCo Analysis: adhfophjkhfbceaeljogehoikdnaalgn

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 3

---

## Sink 1: storage_sync_get_source → chrome_tabs_executeScript_sink

**CoCo Trace:**
```
$FilePath$/media/data2/jianjia/extension_data/unzipped_extensions/adhfophjkhfbceaeljogehoikdnaalgn/opgen_generated_files/bg.js
Line 679    var storage_sync_get_source = {'key':'value'};
Line 922    if (data && data.userkey) {
Line 941    const code = `...(template literal with iframe injection)...`
```

**Code:**
```javascript
// Background script (bg.js, lines 921-960)
chrome.storage.sync.get(['userkey', 'urlExcludeList', 'urlCtrl'], function(data) {
    if (data && data.userkey) {
        let isRun = false;
        const { viewOption, allowUrls, denyUrls } = data.urlCtrl;

        // Control flow based on urlCtrl
        if (viewOption === '보지 않기') {
        } else if (viewOption === '선택된 사이트만 보기') {
            if (allowUrls.find((str) => realUrl.includes(str))) {
                isRun = true;
            }
        } else if (viewOption === '모든 사이트 보기') {
            if (!denyUrls.find((str) => realUrl.includes(str))) {
                isRun = true;
            }
        }

        if (isRun) {
            const code = `
                (function(){
                    if(!document.getElementById("infomax_ifrm_super")){
                        var iframe = document.createElement('iframe');
                        iframe.setAttribute('id', 'infomax_ifrm_super');
                        iframe.src = 'https://chrome.einfomax.co.kr/view/${data.userkey}' // ← hardcoded domain
                        iframe.scrolling = 'no'
                        iframe.frameBorder = 0
                        iframe.style.cssText = '...'
                        document.documentElement.appendChild(iframe)
                    }
                })()
            `;
            chrome.tabs.executeScript(id, { code }); // Executes hardcoded script
        }
    }
});
```

**Classification:** FALSE POSITIVE

**Reason:** Storage data from `storage.sync.get` is used in `executeScript`, but the userkey only goes into a hardcoded backend URL (`https://chrome.einfomax.co.kr/view/${data.userkey}`). This is trusted infrastructure. The executed code itself is hardcoded and not attacker-controlled.

---

## Sink 2 & 3: document_eventListener_ChromeInfomaxEvent → chrome_storage_sync_set_sink

**CoCo Trace:**
```
$FilePath$/media/data2/jianjia/extension_data/unzipped_extensions/adhfophjkhfbceaeljogehoikdnaalgn/opgen_generated_files/cs_0.js
Line 553    function(e) {
Line 564    if (e.detail && e.detail.type === 'save') {
```

**Code:**
```javascript
// Content script (cs_0.js, lines 551-570)
document.addEventListener(
    'ChromeInfomaxEvent',  // ← Custom event, attacker can dispatch
    function(e) {
        if (e.detail && e.detail.type === 'save') {
            chrome.storage.sync.set({ urlCtrl: e.detail }, function() {});  // ← Writes to storage
        }
    },
    false
);
```

**Classification:** FALSE POSITIVE

**Reason:** Incomplete storage exploitation. While an attacker on any webpage can dispatch the custom `ChromeInfomaxEvent` to write arbitrary `urlCtrl` data to `chrome.storage.sync`, this only achieves storage pollution. The urlCtrl data is later retrieved (Sink 1) and used to control whether an iframe is injected, but it does not achieve code execution or data exfiltration. The attacker cannot access the stored data back, and the code executed is hardcoded.
