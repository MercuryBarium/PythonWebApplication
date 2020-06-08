var startDate = document.getElementById('dateFrom')
var endDate = document.getElementById('dateTo')

var now = new Date(Date.now())


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

var before = new Date()
before.setDate(now.getDate() - 31)

var later = new Date()
later.setDate(now.getDate() + 7)

startDate.value = formatDate(before)
endDate.value = formatDate(later)

async function renderOrders() {

    const rawResponse = await fetch('/fetchorder', {
        method: 'POST', 
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({startDate: startDate.value, endDate: endDate.value})
    })

    const cleanResponse = await rawResponse.json()
    console.log(cleanResponse)

    if (cleanResponse['orders'].length > 0) {
        console.log('Yes')
    }
}

$('#filterButton').click(function() {renderOrders()})

renderOrders()