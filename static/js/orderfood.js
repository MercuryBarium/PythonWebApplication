function spinner() {
    var d = document.createElement('div')
    d.classList = [
        'spinner-border',
        'text-primary'
    ]
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

async function placeOrder(orderindex) {
    var confirm = 'Pleas confirm your order: \n\n'
    const labels = document.getElementById('menu ' + orderindex).getElementsByTagName('label')
    const inputs = document.getElementById('menu ' + orderindex).getElementsByTagName('input')
    var payload = {
        day: inputs[0].value,
        order: []
    }

    for (let i = 1; i < inputs.length; i++) {
        food = i - 1
        
        quant = parseInt(inputs[i].value)
        if (quant > 0) {
            payload.order.push({ item: food, amount: quant })
            confirm += labels[food].innerText + ': ' + quant + '\n\n'
        }
    }
    console.log(payload.order[0])
    if (payload.order.length > 0) {
        if (window.confirm(confirm)) {
            console.log(payload)
            $('#msg' + orderindex).html('')
            $('#msg' + orderindex).append(spinner())
            const rawResponse = await fetch('/updateorder', {
                method: 'post',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            })
            const cleanResponse = await rawResponse.json()

            console.log(cleanResponse['opcode'])
            $('#msg' + orderindex).html('')
            if (cleanResponse['opcode'] == 'Success') {
                $('#msg' + orderindex).append(success('Successfully updated order!'))
            } else {
                $('#msg' + orderindex).append(retErrorMSG(cleanResponse['opcode']))
            }
        } 
    } else {
        return
    }
}

incweeks = 0
async function getMenues() {
    const fetchData = await fetch('/fetchmenues', {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ week: incweeks })
    }).catch(err => {
        getMenues()
        return
    }).then(response => response.json()).then(data => {
        var page = document.getElementById('pageCONTENT')
        $('#pageCONTENT').html('')
        var firstRow = document.createElement('div')
        firstRow.className = 'row'
        var info = document.createElement('h1')
        info.innerText = data['year'] + ' W' + data['week']
        firstRow.append(info)
        page.append(firstRow)

        var secondRow = document.createElement('div')
        secondRow.className = 'row'
        for (let i = 0; i < data['menus'].length; i++) {
            if (data['menus'][i]['menu'].length > 0) {
                var orderCOl = document.createElement('div')
                orderCOl.className = 'col border shadow p-3 mb-5 bg-white rounded'
                var menuDate = document.createElement('h3')
                menuDate.innerText = data['menus'][i]['day']
                orderCOl.append(menuDate)
                var orderForm = document.createElement('form')
                orderForm.id = 'menu ' + i
                var formDate = document.createElement('input')
                formDate.type = 'hidden'
                formDate.name = 'date'
                formDate.value = data['menus'][i]['day']
                orderForm.append(formDate)
                for (let x = 0; x < data['menus'][i]['menu'].length; x++) {
                    var group = document.createElement('div')
                    group.className = 'form-group border-bottom'

                    var label = document.createElement('label')
                    label.htmlFor = x
                    label.innerText = data['menus'][i]['menu'][x]
                    var input = document.createElement('input')
                    input.className = 'form-control'
                    input.type = 'number'
                    input.min = 0
                    input.name = x
                    input.value = 0

                    group.append(label)
                    group.append(input)
                    orderForm.append(group)
                }

                var submit = document.createElement('button')
                submit.className = 'btn btn-primary'
                submit.type = 'button'
                submit.innerText = 'Submit'
                submit.onclick = function () {
                    placeOrder(i)
                }
                orderForm.append(submit)

                var msges = document.createElement('div')
                msges.id = 'msg' + i

                orderCOl.append(orderForm)
                orderCOl.append(msges)
                secondRow.append(orderCOl)
            }

        }
        page.append(secondRow)
    })
}
getMenues()