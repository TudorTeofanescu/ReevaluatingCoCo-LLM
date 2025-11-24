# CoCo Analysis: endjefmcpicdnlhdhdjmkcdhnbjaehbb

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1 (XMLHttpRequest_responseText_source → XMLHttpRequest_post_sink)

---

## Sink: XMLHttpRequest_responseText_source → XMLHttpRequest_post_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/endjefmcpicdnlhdhdjmkcdhnbjaehbb/opgen_generated_files/bg.js
Line 332	XMLHttpRequest.prototype.responseText = 'sensitive_responseText';
Line 987	var obj_resp = resp?JSON.parse(resp.substring(resp.indexOf("(")+1,resp.indexOf(")"))):"";
Line 989	var _account = obj_resp.Info.status.split("|");
Line 990-992	var _orgId = _account[1]; var _ownerAcc = _account[0]; var _key = _account[2].substring(6,_account[2].length-4);
Line 995	var _data = "orgId="+_orgId+"&ownerAcc="+_ownerAcc+"&mobilephone="+request.msg.mobilephone+...
```

**Code:**

```javascript
// Background script (script/background.js)
var _domain = "http://quick.test.com/";

function sendUserInfo() {
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "http://127.0.0.1:3366/AccountStatus?callback=cb_loginStatus", true);
    xhr.onreadystatechange = function() {
        if (xhr.readyState == 4) {
            resp = xhr.responseText;  // ← Data from hardcoded localhost endpoint
        }
    }
    xhr.send();
}

function getContentScriptMsg() {
    chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
        if (request.msg) {
            var obj_resp = resp ? JSON.parse(resp.substring(resp.indexOf("(")+1,resp.indexOf(")"))) : "";
            if (typeof(obj_resp) == "object" && (request.msg.mobilephone!="" || request.msg.telphone!="" || request.msg.name!="")) {
                var _account = obj_resp.Info.status.split("|");  // ← From hardcoded localhost
                var _orgId = _account[1];
                var _ownerAcc = _account[0];
                var _key = _account[2].substring(6, _account[2].length-4);
                var timestamp = new Date().getTime();
                var _url = _domain + "htmlApi/getmessage";  // ← Hardcoded backend URL
                var _data = "orgId="+_orgId+"&ownerAcc="+_ownerAcc+"&mobilephone="+request.msg.mobilephone+"&name="+encodeURIComponent(encodeURIComponent(request.msg.name))+"&telphone="+encodeURIComponent(encodeURIComponent(request.msg.telphone))+"&key="+_key+"&t="+timestamp;
                getSourceStatus(_url, _data);  // POST to hardcoded backend
            }
        }
    });
}

function getSourceStatus(url, data) {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", url, true);  // ← Sends to hardcoded backend
    xhr.setRequestHeader("Content-type","application/x-www-form-urlencoded");
    xhr.send(data);
}
```

**Classification:** FALSE POSITIVE

**Reason:** This involves hardcoded backend URLs (trusted infrastructure). The flow is:
1. Extension fetches authentication data from hardcoded localhost endpoint (http://127.0.0.1:3366/AccountStatus)
2. Extension parses account credentials from that response
3. Extension sends data (including credentials from localhost and form data from content script) to hardcoded backend (http://quick.test.com/)

Both the source (localhost:3366) and sink (quick.test.com) are hardcoded trusted infrastructure endpoints controlled by the extension developer. While the content script does send DOM data (company info from 1688.com pages) via chrome.runtime.sendMessage, this data is combined with credentials from the developer's localhost service and sent only to the developer's hardcoded backend. Per the methodology, data flows to/from hardcoded developer backend URLs are treated as trusted infrastructure, not extension vulnerabilities. Compromising the developer's infrastructure is a separate issue from extension vulnerabilities.
