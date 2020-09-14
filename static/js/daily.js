//A simple script that connects to my rest api and retrieves the orders for the day

async function dailyMain() {
    $('#pageCONTENT').html('')
    $('#pageCONTENT').append(spinner())
    const rawFetch = await fetch('/dailyreport', {
        method: 'GET',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
    })
    const cleanFetch = await rawFetch.json()
    console.log(cleanFetch)

    var orders = cleanFetch['orders']
    var rows = []
    for (let i = 0; i < orders.length; i++) {
        rows.push([orders[i]['food'], orders[i]['amount']])
    }

    $('#pageCONTENT').html('')
    $('#pageCONTENT').append(table(['Item', 'Amount'], rows))
}

dailyMain()
$('#daily').click(dailyMain)