$('.smooth-goto').on('click', function () {
    $('html, body').animate({
        scrollTop: $(this.hash).offset().top + 50
    }, 1000);
});

/* ====================  < LINEAR FORM   > ==================== */ 


var $download = $(".download");
var $formScraper = $("#formScraper");

$download.on("click", function(e){
    $(this).text("Downloading...").queue(function() {
        $formScraper.submit(function (e) {
            var form = this;
            e.preventDefault();
            setTimeout(function () {                
                form.submit();
                $download.text("Download");
            }, 800); 
                
        });
    });
});

/* ====================  < CODE MIRROR > ==================== */ 

var darculaTheme = "darcula";


var showCodeWin = CodeMirror.fromTextArea(document.getElementById("showCodeWin"), {
    mode: "python",
    theme: darculaTheme,
    lineNumbers: true,
    tabSize: 2,
    scrollbarStyle: "overlay",
    readOnly: "nocursor",
    inputStyle: "contenteditable",
    showCursorWhenSelecting: true,
    autofocus: false,
    viewportMargin: Infinity
    
});

var showCodeWin = CodeMirror.fromTextArea(document.getElementById("showCodeWin2"), {
    mode: "python",
    theme: darculaTheme,
    lineNumbers: true,
    tabSize: 2,
    scrollbarStyle: "overlay",
    readOnly: "nocursor",
    inputStyle: "contenteditable",
    showCursorWhenSelecting: true,
    autofocus: false,
    viewportMargin: Infinity
    
});



s



