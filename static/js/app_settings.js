var changes = {}
var changes_keys = []
var original_settings = {}

var save_button = document.getElementById('save_changes_button')
var change_info = document.getElementById('unsaved_changes')

function check_if_changed() {
    for (let i = 0; i<changes_keys.length; i++) {
        if (original_settings[changes_keys[i]]['event_enabled'] == changes[changes_keys[i]]['event_enabled']) {
            if (original_settings[changes_keys[i]]['time_of_execution'] == changes[changes_keys[i]]['time_of_execution']){
                changes_keys.splice(i)
            }
        }
    }
    if (changes_keys.length > 0) {
        save_button.disabled = false
        change_info.innerText = `Unsaved Changes: ${changes_keys.length}`
    } else {
        save_button.disabled = true
        change_info.innerText = 'Unsaved Changes: 0'
    }
}

function addChanges(f_element=document.createElement('input')) {
    var setting = f_element.parentNode.parentElement.id
    has_key = false
    for (let i = 0; i < changes_keys.length; i++) {
        if (setting === changes_keys[i]) {
            has_key = true
        }
    }
    if (!has_key) {
        changes_keys.push(setting)
    }

    var inputs = document.getElementById(setting).getElementsByTagName('input')
    changes[setting] = {}
    for (let i = 0; i < inputs.length; i++) {
        if (inputs[i].type === 'checkbox') {
            changes[setting][inputs[i].name] = inputs[i].checked
        } else {
            changes[setting][inputs[i].name] = inputs[i].value
        }
        
    }
    check_if_changed()
    console.log(changes_keys)
}

function input_struct(val, name, label, type) {
    var form_group = document.createElement('div')
    form_group.className = 'form-group m-2'

    var ret_label = document.createElement('label')
    ret_label.htmlFor = name
    ret_label.innerText = label
    ret_label.className = 'm-1'

    var ret_input = document.createElement('input')
    ret_input.type = type
    ret_input.name = name

    if (type === 'checkbox') {
        ret_input.checked = val
    } else {
        ret_input.value = val
    }
    
    ret_input.onchange = function() {
        addChanges(ret_input)
    }

    form_group.append(ret_label)
    form_group.append(ret_input)
    return form_group
}

function form_struct(id) {
    var ret = document.createElement('form')
    ret.className = 'col form-inline border-bottom'
    ret.id = id
    var name = document.createElement('h4')
    name.innerText = id
    ret.append(name)
    return ret
}

async function get_settings() {
    const raw_fetch = await fetch('/get_events', {
        method: 'GET',
        headers: {
            'Accept': 'application/json'
        }
    })

    const clean_fetch = await raw_fetch.json()

    console.log(clean_fetch)
    settings_list = clean_fetch['events']
    for (let i = 0; i<settings_list.length; i++) {
        var form = form_struct(settings_list[i]['name'])
        var enable = input_struct(settings_list[i]['event_enabled'], 'event_enabled', 'Enable: ', 'checkbox')
        var time_of_execution = input_struct(settings_list[i]['time_of_execution'], 'time_of_execution', 'Time: ', 'time')
        var day = document.createElement('input')
        day.type = 'hidden'
        day.name = 'day'
        day.value = settings_list[i]['day']

        if (clean_fetch['day'] === 'any-any-any' || clean_fetch['day'] === 'never') {

        }
        form.append(time_of_execution)
        form.append(enable)
        
        $('#settings_div').append(form)
        if (settings_list[i]['event_enabled'] === 1) {
            original_settings[settings_list[i]['name']] = {
                'time_of_execution': settings_list[i]['time_of_execution'],
                'event_enabled': true
            }
        } else {
            original_settings[settings_list[i]['name']] = {
                'time_of_execution': settings_list[i]['time_of_execution'],
                'event_enabled': false
            }
        }
        
    }
}

get_settings()