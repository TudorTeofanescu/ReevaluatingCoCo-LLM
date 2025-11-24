# CoCo Analysis: lnackbdalieickokiinnbcigkiamojed

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** Multiple (all same flow pattern)

---

## Sink: storage_local_get_source → JQ_obj_html_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/lnackbdalieickokiinnbcigkiamojed/opgen_generated_files/cs_0.js
Line 418: `var storage_local_get_source = { 'key': 'value' };` (framework code)
Line 582: `var items = JSON.parse(result.urldata);`
Line 594: `var texts = items[linkCount]['data']['title'];`
Line 601: `ref.html(texts + " " + "<a href=\""+items[linkCount]['data']['url']+"\">"+ items[linkCount]['data']['url'] +"</a>");`

**Code Flow:**

```javascript
// Content script - cs_0.js Line 581-601
chrome.storage.local.get('urldata', function (result) {
    var items = JSON.parse(result.urldata); // Storage data retrieved

    if (items != null) {
        $(".js-tweet-text").each(function() {
            var url = $(this).attr('data-expanded-url');
            var textData = $(this).text();
            if (url != undefined)
                textData = textData.concat(" ", url);

            matchFilter($(this), textData, function(ref) {
                var texts = items[linkCount]['data']['title'];
                linkCount = linkCount + 1;

                // jQuery HTML sink
                ref.html(texts + " " + "<a href=\""+items[linkCount]['data']['url']+"\">"+
                         items[linkCount]['data']['url'] +"</a>");
            });
            textCount = textCount + 1;
        });
    }
});

// Background script - bg.js Line 976-1007
function getLinksFromSubReddit(subReddit) {
    var xhr = new XMLHttpRequest();
    var url = "http://www.reddit.com/r/" + subReddit + "/.json?";
    xhr.open("GET", url, true);
    xhr.send();
    xhr.onreadystatechange = function() {
        if (xhr.readyState == 4) {
            resp = JSON.parse(xhr.responseText);
            var dataObjects = resp['data']['children'];
            var newItems = JSON.stringify(dataObjects);

            chrome.storage.local.set({"urldata": newItems}, function() {});
        }
    };
}

// Message handler - bg.js (after line 968)
chrome.extension.onRequest.addListener(function(request, sender, sendResponse) {
    if (request.msg == "filter")
        addFilter(request.data);

    if (request.msg == "subReddit") {
        addSubReddit(request.data);
    }
});
```

**Classification:** FALSE POSITIVE

**Reason:** No external attacker entry point. The flow is:
1. Background script fetches data from Reddit API (hardcoded backend URL: reddit.com)
2. Stores Reddit response in `chrome.storage.local` as `urldata`
3. Content script reads `urldata` from storage and uses it in jQuery `.html()` sink

While the extension has a `chrome.extension.onRequest` listener, this is an INTERNAL message handler (not `onMessageExternal`), meaning only the extension's own content scripts can send messages to it, not external attackers. The stored data comes exclusively from Reddit's API, which is the developer's trusted backend infrastructure. According to the methodology, data from hardcoded backend URLs (reddit.com) is not attacker-controlled. There is no path for an external attacker to poison the storage with malicious data.
