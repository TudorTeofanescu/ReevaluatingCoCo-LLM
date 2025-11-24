# CoCo Analysis: paegakmcpjcoihjndpgdbilmjbcjedhd

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 11 (9 Document_element_href → fetch_resource_sink, 2 fetch_source → JQ_obj_html_sink)

---

## Sink 1-9: Document_element_href → fetch_resource_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/paegakmcpjcoihjndpgdbilmjbcjedhd/opgen_generated_files/cs_0.js
Line 20: `this.href = 'Document_element_href';` (CoCo framework code)
Line 659: `var vid = url.href.match(/(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/ ]{11})/i)[1];`
Line 684: `var surl = \`https://video.google.com/timedtext?lang=${lang}&v=${vid}\`;`

**Code:**

```javascript
// Content script (cs_0.js) - Line 655-684
var isOpen = location.href.includes('watch');
if ((titleLink[0] && titleLink[0].href) || isOpen) {
    var url = isOpen ? location : titleLink[0];
    // Extract YouTube video ID using strict regex (exactly 11 characters)
    var vid = url.href.match(/(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/ ]{11})/i)[1];

    if (lyricsEnabled && vid !== lastVid) {
        lastVid = vid;
        processOfficial(vid, defaultCCLang);
    }
}

function processOfficial(vid, lang) {
    // Hardcoded domain, sanitized video ID (11 chars only)
    var surl = `https://video.google.com/timedtext?lang=${lang}&v=${vid}`;
    chrome.runtime.sendMessage(
        { action: "scrape", url: surl },
        data => { /* process subtitles */ }
    );
}
```

**Classification:** FALSE POSITIVE

**Reason:** While the video ID is extracted from the page URL, it's strictly validated by regex to be exactly 11 characters and used only to construct a URL to Google's hardcoded trusted domain (video.google.com). The URL construction is safe and targets trusted infrastructure.

---

## Sink 10-11: fetch_source → JQ_obj_html_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/paegakmcpjcoihjndpgdbilmjbcjedhd/opgen_generated_files/bg.js
Line 265: `var responseText = 'data_from_fetch';` (CoCo framework code)

**Code:**

```javascript
// Content script (cs_0.js) - Line 724-756
function processGenius(title, artist) {
    // Extract and sanitize artist/title from YouTube Music DOM
    // ... sanitization with regex replacements ...

    // Line 750 - Construct URL to hardcoded Genius domain
    url = "https://genius.com/" + url_data + "-lyrics";

    chrome.runtime.sendMessage(
        { action: "scrape", url: url },
        data => {
            var el = $('<div></div>');
            el.html(data);  // Sink: response from genius.com

            var lyrics = $(".lyrics", el).text();
            // ... extract and display lyrics ...
        });
}
```

**Classification:** FALSE POSITIVE

**Reason:** Data flows from hardcoded trusted backend (genius.com). While URL is partially constructed from DOM data (song title/artist), the domain is hardcoded to genius.com, which is the developer's trusted infrastructure for fetching lyrics data.
