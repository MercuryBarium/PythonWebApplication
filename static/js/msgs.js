const thisurl = new URL(location.toString())
function msg(text='None', type='alert-success') {
    var child = document.createElement('div')
    child.className = 'alert ' + type
    cleanText = text.replace(new RegExp('-', 'g'), ' ')
    child.innerText = cleanText
    return child
}
if (thisurl.searchParams.get('success')) {
    $('#msgs').append(msg(thisurl.searchParams.get('success')))
} else if (thisurl.searchParams.get('error')) {
    $('#msgs').append(msg(thisurl.searchParams.get('error'), 'alert-danger'))
}