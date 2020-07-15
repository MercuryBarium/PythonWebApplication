const thisUrl = new URL(location.toString())

async function auto_verify(){
    const email_address = thisUrl.searchParams.get('email')
    const ver_token = thisUrl.searchParams.get('token')

    console.log(email_address)
    console.log(ver_token)

    const raw_response = await fetch('/auto_verify', {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }, 
        body: JSON.stringify({
            email: email_address,
            token: ver_token
        })
    })

    const clean_response = await raw_response.json()
    
    if (clean_response['opcode'] === 'success') {
        $('#status').html('')
        $('#status').append(success('Successfully verified account.'))
    } else {
        $('#status').html('')
        $('#status').append(retErrorMSG('Invalid token or email.'))
    }

}

auto_verify()