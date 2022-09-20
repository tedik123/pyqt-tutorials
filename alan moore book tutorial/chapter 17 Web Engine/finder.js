

function highlight_selection() {
    let tag = document.createElement('found');
    tag.style.backgroundColor = 'lightgreen'
    window.getSelection().getRangeAt(0).surroundContents(tag);
}

function highlight_term(term) {
    let found_tags = document.getElementsByTagName('found');
    //clean up
    while (found_tags.length>0 ) {
        //this clears our wrapper function <found> text </found> from the html
        found_tags[0].outerHTML = found_tags[0].innerHTML;
    }
    let matches = 0;
    //search forward
    while (window.find(term)) {
        highlight_selection()
        matches++;
    }
    //search backward
    while(window.find(term, false, true)) {
        highlight_selection()
        matches++;
    }
    //since java is async python will not be able to get this return value,
    // look back in search text to see how we get it
    return matches
}