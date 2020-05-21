function retLink(name, link) {
    var ret = document.createElement("a")
    ret.className = "nav-link active"
    ret.href = link
    ret.innerText = name
    return ret
}
async function isAdmin(){
    const rawResponse = await fetch("/auth", {
        method: "POST",
        headers: {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    })
    const clean = await rawResponse.json()
    if (clean["code"] == 1) {
        $("#mainNav").append(retLink("Edit Menues", "/admin/editmenues.html"))
        $("#mainNav").append(retLink("View Orders", "/admin/vieworders,html"))

    }
}
isAdmin()