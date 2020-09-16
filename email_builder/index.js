const juice = require("juice")
const fs = require("fs")

const css = fs.readFileSync("src/bulma.min.css", { encoding: "utf-8" })
const outputDir = process.argv[2]
const options = {
    preserveFontFaces: false,
    preserveImportant: false,
    preserveMediaQueries: false,
    preserveKeyFrames: false,
    preservePseudos: false,
}

if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir);
}
console.info(`Compiling base...`)
const baseFile = fs.readFileSync("src/base.html", { encoding: "utf-8" })
const html = juice.inlineContent(baseFile, css, options)
fs.writeFileSync(`${outputDir}/base.html`, html)

fs.readdirSync("src").forEach(name => {
    if (fs.statSync(`src/${name}`).isDirectory()) {
        console.info(`Compiling ${name}...`)
        const file = fs.readFileSync(`src/${name}/email.html`, { encoding: "utf-8" })
        const html = juice.inlineContent(file, css, options)
        const dir = `${outputDir}/${name}`
        if (!fs.existsSync(dir)) {
            fs.mkdirSync(dir)
        }
        fs.writeFileSync(`${outputDir}/${name}/email.html`, html)
    }
})
