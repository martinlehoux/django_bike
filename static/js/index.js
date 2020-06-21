document.querySelectorAll("input[type=file]").forEach(input => {
    input.onchange = () => document.getElementById(`name-${input.name}`).innerText = input.files[0].name
})
