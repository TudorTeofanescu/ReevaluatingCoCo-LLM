# CoCo Analysis: ddkkgafbjffnjndgpiledmgcaokbelnp

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 2 (duplicate detection)

---

## Sink: fetch_source → chrome_storage_local_set_sink (detected twice)

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ddkkgafbjffnjndgpiledmgcaokbelnp/opgen_generated_files/bg.js
Line 265	    var responseText = 'data_from_fetch';
```

**Code:**

```javascript
// CoCo only detected flows in framework mock code (Line 265)
// The actual extension code (after line 963+) shows:

// Background script (bg.js Line 987+)
chrome.runtime.onInstalled.addListener(() => {
    let cpu_model = "";
    let memory = "";

    chrome.storage.sync.get('userid', function (items) {
        var hash = items.userid;
        if (hash) {
            useToken(hash);
        } else {
            hash = getRandomToken();
            chrome.storage.sync.set({userid: hash}, function () {
                useToken(hash);
            });
        }

        function useToken(hash) {
            chrome.system.cpu.getInfo(function (info) {
                cpu_model = info.modelName;
                chrome.storage.local.set({cpu_model: cpu_model});

                chrome.system.memory.getInfo(function (info) {
                    var memory_gb = Math.round(info.capacity / 1024 / 1024 / 1024);
                    memory = info.capacity;
                    chrome.storage.local.set({ram: memory_gb + 'GB'});

                    chrome.system.storage.getInfo(function (info) {
                        chrome.storage.local.set({storage: info});

                        var url = 'https://public-mvdst.ddns.net/services/get_link';

                        // Sending data to hardcoded backend
                        fetch(url, {
                            mode: 'cors',
                            method: 'POST',
                            headers: {
                                'Accept': 'application/json, application/xml, text/plain, text/html, *.*',
                                'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'
                            },
                            body: 'cpu_detected=' + cpu_model + '&ram_detected=' + memory + '&almacenamiento_detected=' + JSON.stringify(info) + '&hash=' + hash
                        }).then(function (response) {
                            return response.text();
                        }).then(function (text) {
                            // Storing response from hardcoded backend
                            chrome.storage.local.set({resultado: text});
                            console.log(text);

                            chrome.tabs.create({
                                url: text,
                                active: true
                            });
                        });
                    });
                });
            });
        }
    });
});
```

**Classification:** FALSE POSITIVE

**Reason:** CoCo only detected flows in framework mock code (Line 265: `var responseText = 'data_from_fetch'`). Examining the actual extension code reveals that it fetches data from a hardcoded backend URL (`https://public-mvdst.ddns.net/services/get_link`) and stores the response in chrome.storage.local. This is a FALSE POSITIVE for two reasons: (1) No external attacker trigger - this code only runs on extension installation (chrome.runtime.onInstalled), not from external messages or DOM events; (2) Data comes FROM hardcoded backend URL (trusted infrastructure) - the extension trusts its own backend server. Compromising the developer's infrastructure is a separate issue from extension vulnerabilities. There is no flow where an attacker can control data going into storage.
