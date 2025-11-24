# CoCo Analysis: golokcohgodgnecheiekdbbeoieegejp

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 4+ (multiple chrome_storage_local_set_sink flows)

---

## Sink: XMLHttpRequest_responseText_source → chrome_storage_local_set_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/golokcohgodgnecheiekdbbeoieegejp/opgen_generated_files/bg.js
Line 332	XMLHttpRequest.prototype.responseText = 'sensitive_responseText'
Line 993	rs = JSON.parse(xhr.responseText)
Line 2159	'isTestPeriod': rs.isTestPeriod
Line 2170	'hideQuickLogin': rs.hideQuickLogin
Line 2165	'extractFlight': rs.extractFlight
```

CoCo detected multiple flows from `XMLHttpRequest_responseText_source` to `chrome_storage_local_set_sink` with different properties: `isTestPeriod`, `hideQuickLogin`, `extractFlight`, and others.

**Code:**

```javascript
// Background script - XHR handler (bg.js Line 985-1003)
function withXHR(rq, func) {
    try {
        var xhr = new XMLHttpRequest();
        xhr.onreadystatechange = function() {
            if (xhr.readyState == 4)  {
                if (xhr.status == 200) {
                    var rs;
                    try {
                        rs = JSON.parse(xhr.responseText); // XHR response parsed
                    } catch (pe) {
                        console.log("Ошибка парсинга ответа: " + pe.message);
                        if ( rq.onError ) {
                            rq.onError("Ошибка парсинга ответа: '" + pe.message +
                                "'. JSON: '" + xhr.responseText + "'", xhr.status);
                        }
                    }
                    if ( rq.onComplete ) {
                        rq.onComplete(rs); // Calls storeAgencyInfo
                    }
                }
            }
        };
        func(xhr);
    } catch (se) {
        console.log("Ошибка соединения с сервером: " + se.message);
    }
}

// Background script - updateAgencyInfo (bg.js Line 2183-2203)
async function updateAgencyInfo(loginAndPassword, updateBalance, callback) {
    getOrderData(function() {});
    var actor = await getActorData();
    getAgencyId(function(agencyId) {
        if ( !agencyId && !loginAndPassword  ) {
            return;
        }
        var payload = loginAndPassword ? JSON.stringify(loginAndPassword) : JSON.stringify({check_auth:""});
        post({
            url: "https://crmtravels.com/"+LOCALE_CODE+"/authorization", // Hardcoded backend URL
            content: payload,
            onComplete: function (rs){
                AG_INF_ERR = 0;
                storeAgencyInfo(rs, function() { // Stores response from crmtravels.com
                    // ...
                });
            }
        });
    });
}

// Background script - storeAgencyInfo (bg.js Line 2130-2178)
function storeAgencyInfo(rs, callback) {
    getValidManagerId(function(managerId) {
        storage.set({
            // Data from hardcoded backend stored
            'isTestPeriod': rs.isTestPeriod,
            'hideQuickLogin': rs.hideQuickLogin,
            'extractFlight': rs.extractFlight,
            // ... other properties
        }, function() {
            console.log('agency info has been saved');
            callback();
        });
    });
}
```

**Manifest.json permissions:**
```json
"permissions": [ "https://crmtravels.com/*", "notifications", "storage", "tabs", "<all_urls>" ]
```

**Classification:** FALSE POSITIVE

**Reason:** Hardcoded backend URLs (trusted infrastructure). The flow is: extension makes XHR request to hardcoded developer backend URL `https://crmtravels.com/`, receives response, and stores it in chrome.storage.local. This is data FROM the developer's own trusted backend server being stored locally. According to the methodology, data from/to hardcoded backend URLs represents trusted infrastructure, and compromising developer infrastructure is separate from extension vulnerabilities. There is no attacker-controlled data in this flow - the data comes from the extension developer's own server which they trust.
