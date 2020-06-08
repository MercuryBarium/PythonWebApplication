var incWEEK = 0

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

function removeSelfAndParent(e) {
    e.parentNode.parentNode.removeChild(e.parentNode)
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

function menitem(item, removable) {
    var formGROUP = document.createElement('div')
    formGROUP.className = 'form-group d-flex justify-content-between'

    var menuINPUT = document.createElement('input')
    menuINPUT.placeholder = 'Type in menu here'
    menuINPUT.type = 'text'
    menuINPUT.className = 'm-1'
    if (item != '') { menuINPUT.value = item }
    formGROUP.append(menuINPUT)
    var remove = document.createElement('button')
    remove.type = 'button'
    remove.innerText = 'X'
    if (removable) {
        remove.className = 'btn btn-danger'
        remove.onclick = function () {
            removeSelfAndParent(remove)
        }
    } else {
        remove.className = 'btn btn-danger disabled'
    }
    formGROUP.append(remove)
    return formGROUP
}

async function removeMenu(menuIndex) {
    if (window.confirm('Are you sure you want delete this menu?')) {
        $('#msg' + menuIndex).html('')
        $('#msg').append(spinner())
        const rawFetch = await fetch('/removemenu', {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }, 
            body: JSON.stringify({
                weekskip: incWEEK,
                day: menuIndex
            })
        }).catch(err => {
            $('#msg' + menuIndex).html('')
            $('#msg' + menuIndex).append(retErrorMSG(err))
            return
        })
        const cleanResponse = await rawFetch.json()
        console.log(cleanResponse['msg'])
        $('#msg' + menuIndex).html('')
        if (cleanResponse['msg'] == 'success') {
            $('#msg' + menuIndex).append(success('Successfully deleted menu.'))
        } else {
            $('#msg' + menuIndex).append(retErrorMSG('500: Internal server error'))
        }
        
    } else {
        return
    }
}

function menCol(date, menuIndex, menu) {
    var menuCOL = document.createElement('div')
    menuCOL.className = 'col border shadow p-3 mb-5 bg-white rounded'
    var colInfo = document.createElement('h3')
    colInfo.innerText = date
    menuCOL.append(colInfo)

    var menuFORM = document.createElement('form')
    menuFORM.id = 'menu ' + menuIndex

    var buttonGroup = document.createElement('div')
    buttonGroup.className = 'm-2 d-flex justify-content-between'

    var addMenu = document.createElement('button')
    addMenu.className = 'btn btn-success'
    addMenu.innerText = 'Add menu'
    addMenu.id = 'addline ' + menuIndex
    addMenu.onclick = function () {
        document.getElementById('menu ' + menuIndex).append(menitem('', true))
    }
    var deleteButton = document.createElement('button')
    deleteButton.className = 'btn btn-danger'
    deleteButton.innerText = 'Delete'
    deleteButton.onclick = function() {
        removeMenu(menuIndex)
    }

    buttonGroup.append(addMenu)
    buttonGroup.append(deleteButton)

    menuCOL.append(buttonGroup)

    if (menu.length == 0) {
        menuFORM.append(menitem('', false))
    } else {
        for (let x = 0; x < menu.length; x++) {
            if (x != 0) {
                menuFORM.append(menitem(menu[x], true))
            } else {
                menuFORM.append(menitem(menu[x], false))
            }

        }
    }

    menuCOL.append(menuFORM)

    var msgrow = document.createElement('div')
    msgrow.id = 'msg' + menuIndex
    menuCOL.append(msgrow)

    return menuCOL
}

async function editmenus(weeknumber) {
    const rawFetch = await fetch('/fetchmenues', {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ week: weeknumber })
    }).catch(err => {
        $('#messages').html('')
        var connectionfailure = document.createElement('div')
        connectionfailure.className = 'alert alert-danger'
        connectionfailure.innerText = err
        $('messages').append(connectionfailure)
        return
    })

    var content = await rawFetch.json()
    //console.log(content)
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
    for (let i = 0; i < content['menus'].length; i++) {
        secondROW.append(menCol(content['menus'][i]['day'], i, content['menus'][i]['menu']))
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
            $('#msg' + i).html('')
            $('#msg' + i).append(spinner())
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
            }).catch(err => {

            })
            const cleanResponse = await updateResponse.json()
            console.log(cleanResponse['opcode'])

            var alerts = document.getElementById('msg' + i)
            $('#msg' + i).html('')
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

