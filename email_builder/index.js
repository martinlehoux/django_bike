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
const baseFile = fs.readFileSync("src/base.html", { encoding: "utf-8" })
const html = juice.inlineContent(baseFile, css, options)
fs.writeFileSync(`${outputDir}/base.html`, html)

fs.readdirSync("src").forEach(name => {
    if (fs.statSync(`src/${name}`).isDirectory()) {
        const file = fs.readFileSync(`src/${name}/email.html`, { encoding: "utf-8" })
        const html = juice.inlineContent(file, css, options)
        fs.writeFileSync(`${outputDir}/${name}/email.html`, html)
    }
})
