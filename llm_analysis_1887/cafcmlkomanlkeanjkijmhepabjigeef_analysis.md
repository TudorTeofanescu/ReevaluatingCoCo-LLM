# CoCo Analysis: cafcmlkomanlkeanjkijmhepabjigeef

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1900 (all same pattern)

---

## Sink: fetch_source → JQ_obj_html_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/cafcmlkomanlkeanjkijmhepabjigeef/opgen_generated_files/bg.js
Line 265	    var responseText = 'data_from_fetch';
Line 985	                const json = text.match(/callback\((.*?)\)/),
Line 986	                      data = JSON.parse(json[1]);
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/cafcmlkomanlkeanjkijmhepabjigeef/opgen_generated_files/cs_0.js
Line 647			for (isbn in data.books){

**Code:**

```javascript
// Background script - bg.js Lines 980-998
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (request.method == "callAPI") {
        const url = "https://api.calil.jp" + request.params;  // Hardcoded API endpoint
        fetch(url)
            .then(response => response.text())
            .then(text => {
                const json = text.match(/callback\((.*?)\)/),
                      data = JSON.parse(json[1]);  // Data from hardcoded backend
                sendResponse(data);  // Send to content script
            })
            .catch(error => console.log('error: ' + error));
        return true;
    }
});

// Content script - cs_0.js Lines 528-563
call_api : function(params) {
    var self = this;
    chrome.runtime.sendMessage({method: "callAPI", params: params}, function(data) {
        self.callback(data);  // Data from api.calil.jp
    });
},
callback : function(data){
    var session = data['session'];
    var conti = data['continue'];
    this.data_cache = data;

    if(this.render){
        this.render.render_books(data);  // Pass data to render
    }
},

// Content script - cs_0.js Lines 642-764
render_books : function(data){
    this.conti = data['continue'];
    var isbn;
    var systemid;

    for (isbn in data.books){
        var csc = this.get_complete_systemid_count(data.books[isbn]);
        for (systemid in data.books[isbn]){
            if (this.filter_system_id == 'all' || this.filter_system_id == systemid){
                switch (this.render_mode) {
                case 'single':
                    this.render_detail(isbn,systemid,data.books[isbn][systemid]);
                    break;
                case 'list':
                    var conti = (csc < this.systemid_list.length);
                    this.render_abstract(isbn,systemid,data.books[isbn][systemid], conti);
                    break;
                }
            }
        }
    }
},

render_detail : function(isbn,systemid,data){
    // ... processing ...
    var text = "";
    for (var i in data.libkey) {
        var status = data.libkey[i];  // Status from api.calil.jp
        // ... color/bgcolor calculation ...
        text += '<div class="calil_libname" style="color:'+ color + '; background-color:'+bgcolor+';">';
        text += '<a href="https://calil.jp/library/search?s='+systemid+'&k='+encodeURIComponent(i)+'">' + i + '</a>';
        text += '<div class="calil_status">';
        text += status;  // Inserting status text
        text += '</div>';
        text += '</div>';
    }

    if (data.reserveurl != "" && total_status != "蔵書なし"){
        text += '<div class="calil_reserve">';
        text += '<a href="'+data.reserveurl+'" target="_blank">予約する</a>';  // URL from API
        text += '</div>';
    }

    $("#"+isbn).find("#"+systemid+"> .prefix").html(text);  // jQuery html() sink
}
```

**Classification:** FALSE POSITIVE

**Reason:** All 1900 detections involve data from the hardcoded backend API (https://api.calil.jp) being used in jQuery .html() sinks. This is trusted infrastructure - api.calil.jp is the official Calil library search API that the extension is designed to integrate with. The extension fetches book availability data from this hardcoded API endpoint and renders it in the page. The data flow is:
1. Content script calls background script with API parameters
2. Background script fetches from hardcoded https://api.calil.jp endpoint
3. Response data is sent back to content script
4. Content script renders the library book data using jQuery .html()

The API endpoint is hardcoded in the background script (Line 981), and the extension has host_permissions only for "https://calil.jp/" and "https://api.calil.jp/" in manifest.json. No external attacker can trigger this flow to use a different API endpoint or inject malicious data. The data comes from the developer's trusted backend infrastructure. Compromising the Calil API infrastructure is a separate issue from extension vulnerabilities.
