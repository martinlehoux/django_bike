document.querySelectorAll("input[type=file]").forEach(input => {
    input.onchange = () => document.getElementById(`name-${input.name}`).innerText = input.files[0].name
})

document.querySelectorAll("button.delete").forEach(button => {
    button.onclick = () => button.parentNode.parentNode.removeChild(button.parentNode)
})

document.querySelectorAll("button[name=modal-open]").forEach(button => {
    button.onclick = () => document.getElementById(button.value).classList.add("is-active")
})

document.querySelectorAll(".modal button[name=modal-close]").forEach(button => {
    button.onclick = () => document.getElementById(button.value).classList.remove("is-active")
})
