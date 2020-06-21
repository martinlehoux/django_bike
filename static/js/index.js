document.querySelectorAll("input[type=file]").forEach(input => {
    input.onchange = () => document.getElementById(`name-${input.name}`).innerText = input.files[0].name
})

document.querySelectorAll("button.delete").forEach(button => {
    button.onclick = () => button.parentNode.parentNode.removeChild(button.parentNode)
})
