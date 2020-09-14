//I use bootstrap so in order to make the rest of the code a bit shorter I made
//this script containing a few functions that returns HTML objects. error msg's etc

function spinner() {
    var d = document.createElement('div')
    d.className = 'spinner-border text-primary'
    
    var spinner = document.createElement('span')
    spinner.className = 'sr-only'
    spinner.innerText = 'Loading...'
    d.append(spinner)
    return d
}

function retErrorMSG(err) {
    var errMSG = document.createElement('div')
    errMSG.className = 'alert alert-danger'
    errMSG.innerText = err
    return errMSG
}

function success(msg) {
    var success = document.createElement('div')
    success.className = 'alert alert-success'
    success.innerText = msg
    return success
}

function table(columns=['Default'], vals=[['Default']]) {
    var thisTable = document.createElement('table')
    thisTable.className = 'table m-2'
        
    var cols = document.createElement('thead')

    for (let i = 0; i < columns.length; i++) {
        var col = document.createElement('th')
        col.innerText = columns[i]
        col.scope = 'col'
        cols.append(col)
    }
    thisTable.append(cols)

    var tBody = document.createElement('tbody')

    for (let i = 0; i < vals.length; i++) {
        var row = document.createElement('tr')
        for (let x = 0; x < vals[i].length; x++) {
            var colVal = document.createElement('td')
            if (x===0) {
                colVal = document.createElement('th')
                colVal.scope = 'row'
            }
            colVal.innerText = vals[i][x]
            row.append(colVal)
        }
        tBody.append(row)
    }
    thisTable.append(tBody)
    return thisTable
}

function formatDate(date){
    year = date.getFullYear()
    month = date.getMonth() + 1
    day = date.getDate()
    if (month < 10) {
        month = `0${month}`
    } 
    if (day < 10) {
        day = `0${day}`
    }
    return `${year}-${month}-${day}`
}