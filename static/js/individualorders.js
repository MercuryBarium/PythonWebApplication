var now = new Date(Date.now())

var before = new Date()
before.setDate(now.getDate() - 31)

var later = new Date()
later.setDate(now.getDate() + 7)


var date_input_from = document.getElementById('dateFrom')
date_input_from.value = formatDate(before)

var date_input_to = document.getElementById('dateTo')
date_input_to.value = formatDate(later)

async function getIndividuals() {
    $('#pageCONTENT').html('')
    $('#pageCONTENT').append(spinner())

    var from = formatDate(new Date(date_input_from.value))
    var to = formatDate(new Date(date_input_to.value))

    const rawFetch = await fetch('/individualreports', {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({'date_from': from, 'date_end': to})
    })

    const cleanFetch = await rawFetch.json()

    individuals = []
    for (let i = 0; i < cleanFetch['individuals'].length; i++) {
        individuals.push([
            cleanFetch['individuals'][i]['name'],
            cleanFetch['individuals'][i]['total']
        ])
    }

    $('#pageCONTENT').html('')
    $('#pageCONTENT').append(table(['Individual', 'Total'], individuals))
}

$('#filterButton').click(getIndividuals)
getIndividuals()