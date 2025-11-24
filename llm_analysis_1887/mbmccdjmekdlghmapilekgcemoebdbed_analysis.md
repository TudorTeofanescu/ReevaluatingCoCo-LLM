# CoCo Analysis: mbmccdjmekdlghmapilekgcemoebdbed

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 12 (all variants of the same flow pattern)

---

## Sink: storage_local_get_source → JQ_obj_val_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/mbmccdjmekdlghmapilekgcemoebdbed/opgen_generated_files/cs_3.js
Line 418: var storage_local_get_source = {'key': 'value'};
Line 472: console.log(content.PFSData);
Line 480: $.each(content.PFSData.grades,function(key,value) {
Line 483: fieldvalue.val(content.PFSData.grades[key].score);

**Code:**

```javascript
// cs_0.js (course_matls.js) - Runs on Schoology website
// User clicks "Copy Grades" button added by extension
$(".PFSButton").off('click').on('click',function() {
    var type = $(this).closest(".item-info").prev(".item-icon").attr('class').split(" ")[2];
    var courseid = window.location.pathname.split("/")[2];
    var grades = new Array();

    // Extension makes AJAX request to Schoology
    $.ajax({
        dataType: 'text',
        url: window.location.origin + '/assignment/'+assignmentid+'/info', // Schoology URL
        data: { ajax: 1, f: '' },
        success: function(contents){
            var html = $.parseHTML(contents); // Parse Schoology HTML response
            var gradeswrapper = $(html).find(".right-block-big");
            gradeswrapper.find(".student-info").each(function() {
                var name = $(this).find(".student-name")[0].innerText;
                var grade = $(this).find(".grade")[0].innerText;
                grades.push({name:name,score:grade.split("/")[0]}); // Extract grade data
            });
            var syncdataarray = {'grades': grades,'assgn_name':assignment_name,'column_header':column_header,'duedate':date,'points':maxpoints,'factor':factor};
            chrome.storage.local.set({'PFSData':syncdataarray}, function() {}); // Store grades
        }
    });
});

// cs_3.js (assgn_gradeassignment.js) - Runs on Genesis website
// User clicks "Paste from Schoology" button
$("#PFS-Grade").off('click').on('click',function() {
    chrome.storage.local.get('PFSData',function(content) {
        console.log(content.PFSData);
        $(".listroweven,.listrowodd").each(function() {
            var sname = $(this).find("a[title='View Student Details']").text().trim();
            var fieldvalue = $(this).find("input[id^='fldGrade']");
            $.each(content.PFSData.grades,function(key,value) {
                if (content.PFSData.grades[key].name.trim() == sname) {
                    fieldvalue.val(content.PFSData.grades[key].score); // jQuery .val() sink
                    var event = new Event('change');
                    fieldvalue[0].dispatchEvent(event);
                }
            });
        });
    });
});
```

**Classification:** FALSE POSITIVE

**Reason:** No external attacker trigger. The flow is initiated by user actions:
1. User clicks "Copy Grades" button on Schoology (extension's own UI element)
2. Extension fetches grade data from Schoology via AJAX and stores it
3. User clicks "Paste from Schoology" button on Genesis (extension's own UI element)
4. Extension retrieves stored data and populates form fields

Both entry points require explicit user interaction with buttons added by the extension itself. User actions in the extension's own UI (clicking extension-added buttons) are NOT attacker-controlled. The data source is Schoology's grade system (trusted for this extension's legitimate purpose), and the sink (jQuery .val()) simply populates form input fields. This is the extension's intended functionality - copying grades from one educational system to another - not a vulnerability exploitable by an external attacker.
