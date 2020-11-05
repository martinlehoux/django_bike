MARTOR_TOOLBAR_BUTTONS = [
    "bold",
    "italic",
    "horizontal",
    "heading",
    "pre-code",
    "blockquote",
    "unordered-list",
    "ordered-list",
    "link",
    "emoji",
    "help",
]
MARTOR_ENABLE_LABEL = True
MARTOR_MARKDOWN_EXTENSIONS = [
    "markdown.extensions.extra",
    "markdown.extensions.nl2br",
    "markdown.extensions.smarty",
    "markdown.extensions.fenced_code",
    # Custom markdown extensions.
    "martor.extensions.urlize",
    # 'martor.extensions.del_ins',      # ~~strikethrough~~ and ++underscores++
    # 'martor.extensions.mention',      # to parse markdown mention
    "martor.extensions.emoji",  # to parse markdown emoji
    # 'martor.extensions.mdx_video',    # to parse embed/iframe video
    "martor.extensions.escape_html",  # to handle the XSS vulnerabilities
    "apps.extensions.martor_bulma",
]
