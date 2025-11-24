# CoCo Analysis: heebikahehkkpfekldgnlafenjneaepc

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: XMLHttpRequest_responseText_source → XMLHttpRequest_url_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/heebikahehkkpfekldgnlafenjneaepc/opgen_generated_files/bg.js
Line 332: XMLHttpRequest.prototype.responseText = 'sensitive_responseText'
Line 1206: var cookieServer = JSON.parse(data.replace('null(',' ').replace(')',' ')).passportServerEc;
Line 1208: var loginUrl = global_domain+"/passwidge/batch?cookie="+ cookieServer;

**Code:**

```javascript
// Hardcoded backend domain
var global_domain = 'http://www.tuyuepai.com', // ← hardcoded trusted infrastructure

// First XMLHttpRequest to hardcoded backend
var ZCOOL_PASSPORT_URL = global_domain+'/passwidge/getcookie'; // ← http://www.tuyuepai.com/passwidge/getcookie
getJsonpPicking(ZCOOL_PASSPORT_URL, ZcoolCb);

function ZcoolCb(data) {
    if(data!=null){
        // ← data from hardcoded backend
        var cookieServer = JSON.parse(data.replace('null(',' ').replace(')',' ')).passportServerEc;
        if(!isEmpty(cookieServer)) {
            // Second XMLHttpRequest - still to same hardcoded backend
            var loginUrl = global_domain+"/passwidge/batch?cookie="+ cookieServer; // ← http://www.tuyuepai.com/passwidge/batch
            getJsonpPicking(loginUrl, casCb); // ← sink
        }
    }
}

function getJsonpPicking(url, callback) {
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function(data) {
        if (xhr.readyState == 4) {
            if (xhr.status == 200) {
                callback(xhr.responseText);
            }
        }
    }
    xhr.open('GET', url, true);
    xhr.send();
}
```

**Classification:** FALSE POSITIVE

**Reason:** Data flows FROM hardcoded backend URL (http://www.tuyuepai.com/passwidge/getcookie) → used to construct another URL → sent TO same hardcoded backend (http://www.tuyuepai.com/passwidge/batch). Both source and sink URLs are hardcoded to the developer's trusted infrastructure. The developer trusts their own backend servers. No attacker-controlled data in the flow - this is internal communication between extension and its own backend.
