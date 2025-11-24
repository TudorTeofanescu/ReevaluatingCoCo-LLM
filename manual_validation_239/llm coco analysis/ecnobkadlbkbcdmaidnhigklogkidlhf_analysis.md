# CoCo Analysis: ecnobkadlbkbcdmaidnhigklogkidlhf

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 64 (all variations of the same flow)

---

## Sink: cs_window_eventListener_message → jQuery_ajax_settings_data_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ecnobkadlbkbcdmaidnhigklogkidlhf/opgen_generated_files/cs_0.js
Line 604: `window.addEventListener("message", function(e){`
Line 605: `if(e.data.fun == "syn1688ProductFromList"){`
Line 608: `portSyn1688ProductFromList.postMessage({data:e.data.data});`

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ecnobkadlbkbcdmaidnhigklogkidlhf/opgen_generated_files/bg.js
Line 1045-1049: HTML entity replacement in content
Line 1062: jQuery ajax with data field

**Code:**

```javascript
// Content script (content.js, lines 1571-1606)
window.addEventListener("message", function (e) {
    if (e.data.fun == "translate") {
        port.postMessage({
            resultFun: e.data.resultFun,
            dataId: e.data.dataId,
            data: e.data.data, // ← attacker-controlled
            sl: e.data.sl,
            tl: e.data.tl
        });
    }
    // ... other handlers
}, false);

// Background script (background.js, lines 1084-1089)
chrome.runtime.onConnect.addListener(function(port) {
    port.onMessage.addListener(function(request) {
        if(port.name == "transPage"){
            translate(request.data, request.sl, request.tl, function(res){
                port.postMessage({dataId: request.dataId, data:res, resultFun:request.resultFun, languageCode: request.tl});
            });
        }
        // ... other handlers
    });
});

// Background script translate function (background.js, lines 1044-1076)
function translate(content, from, to, callback){
    content = content.replace(/&quot;/g, '"');
    content = content.replace(/&amp;/g, '&');
    content = content.replace(/&lt;/g, '<');
    content = content.replace(/&gt;/g, '>');
    content = content.replace(/&nbsp;/g, ' ');

    var turl = "https://translate.google.cn/_/TranslateWebserverUi/data/batchexecute..."; // ← Hardcoded URL
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-language": "en,zh-CN;q=0.9,zh;q=0.8",
        "content-type": "application/x-www-form-urlencoded;charset=UTF-8"
    }
    $.ajax({
        type: "POST",
        url: turl, // ← Hardcoded Google Translate URL
        headers: headers,
        dataType: "text",
        data: {"f.req": "[[[\"MkEWBc\",\"[[\\\""+escapeJquery(content)+"\\\",\\\"auto\\\",\\\""+to+"\\\",true],[null]]\",null,\"generic\"]]]"}, // ← Attacker data in POST body
        success: function(res) {
            var result = "";
            res = "[\"wrb.fr\",\"MkEWBc\"," + res.split("[\"wrb.fr\",\"MkEWBc\",")[1];
            res = res.split(",null,null,null,\"generic\"]")[0] + ",null,null,null,\"generic\"]";
            var obj = JSON.parse(res);
            var obj2 = JSON.parse(obj[2]);
            for(var i = 0; i < obj2[1][0][0][5].length; i++){
                result += obj2[1][0][0][5][i][0];
            }
            result = result.replace(/\n/g, "\r\n");
            callback(result);
        }
    });
}
```

**Classification:** FALSE POSITIVE

**Reason:** This is attacker-controlled data sent TO a hardcoded backend URL (Google Translate API at `https://translate.google.cn/...`). The attacker from any webpage can trigger the window.postMessage listener and send arbitrary data to be translated, but the data is sent to Google's trusted infrastructure, not an attacker-controlled destination. According to the methodology, data TO hardcoded backend URLs is trusted infrastructure and does not constitute a vulnerability - compromising Google Translate's infrastructure is a separate issue from extension vulnerabilities. The URL is hardcoded (line 1051), so the attacker cannot perform SSRF. All 64 CoCo detections are variations of this same flow with different message handlers calling the same translate() function or similar patterns.
