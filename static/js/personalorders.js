var startDate = document.getElementById('dateFrom')
var endDate = document.getElementById('dateTo')

var now = new Date(Date.now())

var days = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]

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

function getOrCreateWeekDiv(id) {
    if (document.getElementById(id)) {
        return document.getElementById(id)
    } else {
        var ret = document.createElement('div')
        ret.id = id
        ret.className = 'container border border-primary m-2'

        var weekAndYear = document.createElement('div')
        weekAndYear.className = 'border-bottom'
        var name = document.createElement('h2')
        name.innerText = id
        weekAndYear.append(name)
        ret.append(weekAndYear)

        var theOrders = document.createElement('div')
        theOrders.className = 'row row-cols-1'
        ret.append(theOrders)

        $('#pageCONTENT').append(ret)
        return ret
    }
}

function genOrderCol(order) {
    foodorders = order['foodorder']
    menu = order['menu']
    
    var thisCol = document.createElement('div')
    thisCol.className = 'col row-cols-1 m-1 border-bottom'

    var row_1 = document.createElement('div')
    row_1.className = 'col'
    var name = document.createElement('h4')

    var dayname = new Date(order['day'])

    name.innerText = days[dayname.getDay()] 
    row_1.append(name)
    thisCol.append(row_1)

    var row_2 = document.createElement('div')
    row_2.className = 'col'

    for (let i = 0; i < foodorders.length; i++) {
        var item = foodorders[i]['item']
        var amount = foodorders[i]['amount']

        var itemRow = document.createElement('div')
        itemRow.className = 'col border-bottom m-1'

        var menuText = document.createElement('h5')
        menuText.innerText = menu[item] + ':  '

        var span = document.createElement('span')
        span.className = 'badge badge-secondary'
        span.innerText = amount

        menuText.append(span)
        itemRow.append(menuText)
        row_2.append(itemRow)
    }
    thisCol.append(row_2)
    return thisCol
}

async function renderOrders() {
    $('#pageCONTENT').html('')
    $('#pageCONTENT').append(spinner())
    const rawResponse = await fetch('/fetchorder', {
        method: 'POST', 
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({startDate: startDate.value, endDate: endDate.value})
    })

    const cleanResponse = await rawResponse.json()
    const fetchedOrders = cleanResponse['orders']
    console.log(cleanResponse)
    $('#pageCONTENT').html('')

    for (let i = fetchedOrders.length-1; i >= 0; i--) {
        var year = fetchedOrders[i]['year']
        var week = fetchedOrders[i]['weeknumber']

        getOrCreateWeekDiv(`${year} Week: ${week}`).lastChild.append(genOrderCol(fetchedOrders[i]))
    }
}

$('#filterButton').click(function() {renderOrders()})

renderOrders()