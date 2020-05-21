var incWEEK = 0
function loading() {
    $('#')
}

async function editmenus(weeknumber) {
    const rawFetch = await fetch('/fetchmenues', {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ week: weeknumber })
    })

    var content = await rawFetch.json()
    console.log(content)
    var pageCONTENT = document.getElementById('pageCONTENT')
    $('#pageCONTENT').html('')
    pageCONTENT.className = 'container'

    var topRow = document.createElement('div')
    topRow.className = 'row border-bottom'

    var colOne = document.createElement('div')
    colOne.className = 'col'
    var previous = document.createElement('button')
    previous.type = 'button'
    previous.className = 'btn btn-primary'
    previous.innerText = 'Previous Week'
    previous.onclick = function () {
        incWEEK -= 1
        editmenus(incWEEK)
    }
    colOne.append(previous)
    topRow.append(colOne)

    var colTwo = document.createElement('div')
    colTwo.className = 'col'
    var menuInfo = document.createElement('h1')
    menuInfo.innerText = content['year'] + ' W' + content['week']
    colTwo.append(menuInfo)
    topRow.append(colTwo)

    var colThree = document.createElement('div')
    colThree.className = 'col'
    var NextWeek = document.createElement('button')
    NextWeek.className = 'btn btn-primary'
    NextWeek.innerText = 'Next Week'
    NextWeek.onclick = function () {
        incWEEK += 1
        editmenus(incWEEK)
    }
    colThree.append(NextWeek)
    topRow.append(colThree)

    pageCONTENT.append(topRow)

    var secondROW = document.createElement('div')
    secondROW.className = 'row'
    console.log(content['menus'].length)
    for (let i = 0; i < content['menus'].length; i++) {
        var menuCOL = document.createElement('div')
        menuCOL.className = 'col border shadow p-3 mb-5 bg-white rounded'
        var colInfo = document.createElement('h3')
        colInfo.innerText = content['menus'][i]['day']
        menuCOL.append(colInfo)

        var menuFORM = document.createElement('form')
        menuFORM.id = 'menu ' + i

        var addMenu = document.createElement('button')
        addMenu.className = 'btn btn-success'
        addMenu.innerText = 'Add menu'
        addMenu.id = 'addline ' + i
        addMenu.onclick = function () {
            var formGROUP = document.createElement('div')
            formGROUP.className = 'form-group'
            var menuINPUT = document.createElement('input')
            menuINPUT.placeholder = 'Type in menu here'
            menuINPUT.type = 'text'
            formGROUP.append(menuINPUT)
            document.getElementById('menu ' + i).append(formGROUP)
        }
        menuCOL.append(addMenu)

        if (content['menus'][i]['menu'].length == 0) {
            var formGROUP = document.createElement('div')
            formGROUP.className = 'form-group'
            var menuINPUT = document.createElement('input')
            menuINPUT.placeholder = 'Type in menu here'
            menuINPUT.type = 'text'
            formGROUP.append(menuINPUT)
            menuFORM.append(formGROUP)
        } else {
            for (let x = 0; x < content['menus'][i]['menu'].length; x++) {
                var formGROUP = document.createElement('div')
                formGROUP.className = 'form-group'
                var menuINPUT = document.createElement('input')
                menuINPUT.placeholder = 'Type in menu here'
                menuINPUT.type = 'text'
                menuINPUT.value = content['menus'][i]['menu'][x]
                formGROUP.append(menuINPUT)
                menuFORM.append(formGROUP)
            }
        }


        menuCOL.append(menuFORM)

        secondROW.append(menuCOL)
    }
    pageCONTENT.append(secondROW)

    var lastROW = document.createElement('div')
    lastROW.className = 'row'

    var btnCol = document.createElement('div')
    btnCol.className = 'col'
    var UpdateMenues = document.createElement('button')
    UpdateMenues.className = 'btn btn-primary'
    UpdateMenues.innerText = 'Update Menues'
    UpdateMenues.onclick = async function () {
        for (let i = 0; i < 5; i++) {
            var menuFORM = document.getElementById('menu ' + i)
            var payload = {
                'year': content['year'],
                'week': content['week'],
                'day': i,
                'menu': []
            }
            var inputs = menuFORM.getElementsByTagName('input')
            for (let x = 0; x < inputs.length; x++) {
                if (inputs[x].value.length > 0) {
                    payload['menu'][x] = inputs[x].value
                }
            }

            const updateResponse = await fetch('/updatemenu', {
                method: 'post',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            })
            const cleanResponse = await updateResponse.json()
            console.log(cleanResponse['opcode'])

            var alerts = document.getElementById('messages')
            alerts.innerHTML = ''
            var child = document.createElement('div')
            if (cleanResponse['opcode'] == 'success') {
                child.className = 'alert alert-success'
                child.textContent = 'Successfully edited menu'
            } else {
                child.className = 'alert alert-danger'
                child.innerText = cleanResponse['opcode']
            }
            alerts.appendChild(child)
        }
    }
    btnCol.append(UpdateMenues)
    lastROW.append(btnCol)
    pageCONTENT.append(lastROW)

}
editmenus(incWEEK)
