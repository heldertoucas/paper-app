-- ==============================================================================
-- PROJECT PAPERCLIP: macOS Edition (Hammerspoon)
-- ==============================================================================

local paperclip = {}

-- Configuration
paperclip.hotkey = {"cmd", "shift", "space"}
paperclip.destination_dir = os.getenv("HOME") .. "/Dev/obsidian-ht/00-inbox/mac/"
paperclip.width = 580
paperclip.height = 400
paperclip.domains = {"system", "pessoal", "cmlisboa", "cmlisboa", "freelance"}
paperclip.current_domain_index = 1

-- State
paperclip.last_context = ""
paperclip.last_process = ""
paperclip.is_visible = false

-- Create destination directory if it doesn't exist
hs.fs.mkdir(paperclip.destination_dir)

-- HTML/CSS for the UI (Warm Paper Theme)
local html_template = [=[
<!DOCTYPE html>
<html>
<head>
    <style>
        :root {
            --bg-main: #FDFBF7;
            --text-primary: #2C2825;
            --accent: #D97706;
            --muted: #8C867D;
            --editor-bg: #FDFBF7;
        }
        body {
            background-color: var(--bg-main);
            color: var(--text-primary);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            margin: 0;
            padding: 0;
            overflow: hidden;
            border: 1px solid #E5E1D8;
            border-radius: 12px;
        }
        .header {
            display: flex;
            padding: 12px 16px;
            background: rgba(0,0,0,0.02);
            border-bottom: 1px solid rgba(0,0,0,0.05);
        }
        .tab {
            font-size: 11px;
            color: var(--muted);
            margin-right: 15px;
            cursor: pointer;
            font-weight: 500;
            text-transform: uppercase;
        }
        .tab.active {
            color: var(--accent);
            border-bottom: 2px solid var(--accent);
        }
        textarea {
            width: 100%;
            height: 300px;
            background: var(--editor-bg);
            border: none;
            outline: none;
            padding: 20px;
            font-family: "SF Mono", "Fira Code", monospace;
            font-size: 14px;
            color: var(--text-primary);
            box-sizing: border-box;
            resize: none;
        }
        .footer {
            padding: 8px 16px;
            font-size: 11px;
            color: var(--muted);
            border-top: 1px solid rgba(0,0,0,0.05);
            display: flex;
            justify-content: space-between;
        }
        /* Templates Menu Styles */
        .templates-menu {
            position: absolute;
            bottom: 45px;
            left: 20px;
            background: #FDFBF7;
            border: 1px solid #E5E1D8;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            display: none;
            flex-direction: column;
            z-index: 1000;
            width: 250px;
            overflow: hidden;
        }
        .template-item {
            padding: 8px 12px;
            font-size: 12px;
            cursor: pointer;
            color: var(--text-primary);
            transition: background-color 0.1s ease;
        }
        .template-item:hover, .template-item.active {
            background-color: rgba(0,0,0,0.04);
            color: var(--accent);
        }
    </style>
</head>
<body>
    <div class="header" id="tabs">
        <div class="tab active" onclick="setDomain(1)">1: INBOX</div>
        <div class="tab" onclick="setDomain(2)">2: FAMÍLIA</div>
        <div class="tab" onclick="setDomain(3)">3: PASSAPORTE</div>
        <div class="tab" onclick="setDomain(4)">4: FUTURO</div>
        <div class="tab" onclick="setDomain(5)">5: FREELANCE</div>
        <div class="tab" onclick="showHelp()">?</div>
    </div>
    <textarea id="editor" autofocus placeholder="Write or speak..."></textarea>
    
    <div id="templates-menu" class="templates-menu">
        <div class="template-item active" data-index="0">Email: Follow-up</div>
        <div class="template-item" data-index="1">Email: Meeting Minutes</div>
        <div class="template-item" data-index="2">Code: Task Ref</div>
    </div>

    <div class="footer">
        <span id="status">Ready</span>
        <span>Cmd+Enter to Save</span>
    </div>

    <script>
        const templates = [
            {
                name: "Email: Follow-up",
                text: "Dear [Name],\n\nFollowing up on our conversation regarding..."
            },
            {
                name: "Email: Meeting Minutes",
                text: "## Meeting Minutes\nDate: " + new Date().toISOString().split('T')[0] + "\nParticipants: \n\n### Actions:\n- [ ] "
            },
            {
                name: "Code: Task Ref",
                text: "" // Dynamically filled by lua context
            }
        ];
        
        let templatesActive = false;
        let activeTemplateIndex = 0;

        function setDomain(idx) {
            const tabs = document.querySelectorAll('.tab');
            tabs.forEach((t, i) => {
                if (i === idx-1) t.classList.add('active');
                else t.classList.remove('active');
            });
            window.webkit.messageHandlers.paperclip.postMessage({action: 'setDomain', index: idx});
        }
        function updateContent(text) {
            document.getElementById('editor').value = text;
        }
        function showHelp() {
            const helpText = "PAPERCLIP MAC SHORTCUTS\n\n" +
                "GENERAL:\n" +
                "Cmd+Enter  - Save & Close\n" +
                "Esc        - Hide Window\n\n" +
                "CAPTURE:\n" +
                "Cmd+[1-5]  - Switch Domains\n" +
                "Cmd+Shift+V- Clean Paste\n" +
                "Cmd+Alt+V  - Paste as Markdown\n" +
                "Cmd+J      - Templates Menu\n\n" +
                "FORMATTING:\n" +
                "Cmd+T      - Insert Timestamp\n" +
                "Cmd+L      - Checklist Item\n" +
                "Cmd+K      - Wrap in [[Wiki-link]]";
            document.getElementById('editor').value = helpText;
            document.getElementById('status').innerText = "Help Mode";
        }

        function insertText(text) {
            const el = document.getElementById('editor');
            const start = el.selectionStart;
            const end = el.selectionEnd;
            const val = el.value;
            el.value = val.substring(0, start) + text + val.substring(end);
            el.selectionStart = el.selectionEnd = start + text.length;
            el.focus();
        }

        function wrapSelection(prefix, suffix) {
            const el = document.getElementById('editor');
            const start = el.selectionStart;
            const end = el.selectionEnd;
            const val = el.value;
            const selected = val.substring(start, end);
            const text = prefix + selected + suffix;
            el.value = val.substring(0, start) + text + val.substring(end);
            el.selectionStart = start + prefix.length;
            el.selectionEnd = el.selectionStart + selected.length;
            el.focus();
        }

        function convertHtmlToMd(html) {
            let md = html;
            md = md.replace(/<a [^>]*href=["']([^"']+)["'][^>]*>(.*?)<\/a>/gis, "[$2]($1)");
            md = md.replace(/<(strong|b)>(.*?)<\/\1>/gis, "**$2**");
            md = md.replace(/<(em|i)>(.*?)<\/\1>/gis, "*$2*");
            md = md.replace(/<li[^>]*>(.*?)<\/li>/gis, "- $1\n");
            md = md.replace(/<h1[^>]*>(.*?)<\/h1>/gis, "# $1\n");
            md = md.replace(/<h2[^>]*>(.*?)<\/h2>/gis, "## $1\n");
            md = md.replace(/<h3[^>]*>(.*?)<\/h3>/gis, "### $1\n");
            md = md.replace(/<br\s*\/?>/gis, "\n");
            md = md.replace(/<p[^>]*>(.*?)<\/p>/gis, "$1\n\n");
            md = md.replace(/<[^>]+>/g, "");
            md = md.replace(/&nbsp;/g, " ").replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&quot;/g, '"');
            return md.trim();
        }

        function setTaskRefTemplate(lastProcess, lastContext) {
            templates[2].text = "\n> [!TASK] Ref: " + lastProcess + "\n> " + lastContext + "\n";
        }

        function toggleTemplates() {
            const menu = document.getElementById('templates-menu');
            templatesActive = !templatesActive;
            if (templatesActive) {
                menu.style.display = 'flex';
                updateActiveTemplateHighlight();
            } else {
                menu.style.display = 'none';
            }
        }

        function updateActiveTemplateHighlight() {
            const items = document.querySelectorAll('.template-item');
            items.forEach((item, idx) => {
                if (idx === activeTemplateIndex) {
                    item.classList.add('active');
                } else {
                    item.classList.remove('active');
                }
            });
        }

        function triggerTemplateInsert() {
            insertText(templates[activeTemplateIndex].text);
            toggleTemplates();
        }

        document.getElementById('editor').addEventListener('keydown', (e) => {
            if (templatesActive) {
                if (e.key === 'ArrowDown') {
                    e.preventDefault();
                    activeTemplateIndex = (activeTemplateIndex + 1) % templates.length;
                    updateActiveTemplateHighlight();
                    return;
                }
                if (e.key === 'ArrowUp') {
                    e.preventDefault();
                    activeTemplateIndex = (activeTemplateIndex - 1 + templates.length) % templates.length;
                    updateActiveTemplateHighlight();
                    return;
                }
                if (e.key === 'Enter') {
                    e.preventDefault();
                    triggerTemplateInsert();
                    return;
                }
                if (e.key === 'Escape') {
                    e.preventDefault();
                    toggleTemplates();
                    return;
                }
            }

            if (e.metaKey && e.key === 'Enter') {
                window.webkit.messageHandlers.paperclip.postMessage({
                    action: 'save', 
                    content: document.getElementById('editor').value
                });
            }
            if (e.key === 'Escape') {
                window.webkit.messageHandlers.paperclip.postMessage({action: 'hide'});
            }
            if (e.metaKey && e.key >= '1' && e.key <= '5') {
                setDomain(parseInt(e.key));
            }
            if (e.metaKey && e.key === 't') {
                e.preventDefault();
                const now = new Date();
                insertText(now.getHours().toString().padStart(2, '0') + ":" + now.getMinutes().toString().padStart(2, '0') + ": ");
            }
            if (e.metaKey && e.key === 'l') {
                e.preventDefault();
                insertText("- [ ] ");
            }
            if (e.metaKey && e.key === 'k') {
                e.preventDefault();
                wrapSelection("[[", "]]");
            }
            if (e.metaKey && e.shiftKey && e.key === 'V') {
                e.preventDefault();
                window.webkit.messageHandlers.paperclip.postMessage({action: 'cleanPaste'});
            }
            if (e.metaKey && e.altKey && e.key === 'v') {
                e.preventDefault();
                window.webkit.messageHandlers.paperclip.postMessage({action: 'smartPaste'});
            }
            if (e.metaKey && e.key === 'j') {
                e.preventDefault();
                toggleTemplates();
            }
        });

        // Click handler for templates
        document.querySelectorAll('.template-item').forEach(item => {
            item.addEventListener('click', () => {
                activeTemplateIndex = parseInt(item.getAttribute('data-index'));
                triggerTemplateInsert();
            });
        });
    </script>
</body>
</html>
]=]

-- Setup User Content Controller for JS->Lua communication
local ucc = hs.webview.usercontent.new("paperclip")
ucc:setCallback(function(message)
    local body = message.body
    if body.action == "save" then
        paperclip.saveNote(body.content)
    elseif body.action == "hide" then
        paperclip.hide()
    elseif body.action == "setDomain" then
        paperclip.current_domain_index = body.index
        paperclip.populateYAML(body.content)
    elseif body.action == "cleanPaste" then
        local text = hs.pasteboard.getContents()
        if text then
            text = text:gsub("\r\n", "\n"):gsub("\n\n\n+", "\n\n")
            paperclip.webview:evaluateJavaScript(string.format("insertText(%q)", text:trim()))
        end
    elseif body.action == "smartPaste" then
        local html = hs.pasteboard.readStringForType("public.html")
        if html then
            paperclip.webview:evaluateJavaScript(string.format("insertText(convertHtmlToMd(%q))", html))
        else
            local text = hs.pasteboard.getContents()
            paperclip.webview:evaluateJavaScript(string.format("insertText(%q)", text or ""))
        end
    end
end)

-- Create WebView
paperclip.webview = hs.webview.new({x = 0, y = 0, w = paperclip.width, h = paperclip.height}, {
    developerExtrasEnabled = true
}, ucc)
paperclip.webview:windowStyle({"borderless", "titled"})
paperclip.webview:shadow(true)
paperclip.webview:level(hs.drawing.windowLevels.mainMenu)
paperclip.webview:html(html_template)

-- Logic: Capture Context
function paperclip.captureContext()
    local app = hs.application.frontmostApplication()
    paperclip.last_process = app:name()
    paperclip.last_context = app:focusedWindow():title()

    -- Browser URL Extraction (Safari/Chrome via AppleScript)
    if paperclip.last_process == "Safari" then
        local ok, url = hs.applescript.appleScript('tell application "Safari" to return URL of front document')
        if ok then paperclip.last_context = url end
    elseif paperclip.last_process == "Google Chrome" then
        local ok, url = hs.applescript.appleScript('tell application "Google Chrome" to return URL of active tab of front window')
        if ok then paperclip.last_context = url end
    end
    
    -- Inject context into templates inside JS
    paperclip.webview:evaluateJavaScript(string.format("setTaskRefTemplate(%q, %q)", paperclip.last_process, paperclip.last_context))
end

-- Logic: Populate YAML
function paperclip.populateYAML(existingContent)
    local yaml = "---\n"
    yaml = yaml .. "title: \n"
    yaml = yaml .. "type: source\n"
    yaml = yaml .. "domain: " .. paperclip.domains[paperclip.current_domain_index] .. "\n"
    yaml = yaml .. "context: " .. paperclip.last_process .. "\n"
    if paperclip.last_context:match("^http") then
        yaml = yaml .. "source: " .. paperclip.last_context .. "\n"
    end
    yaml = yaml .. "status: draft\n"
    yaml = yaml .. "created: " .. os.date("%Y-%m-%d") .. "\n"
    yaml = yaml .. "---\n\n"
    
    paperclip.webview:evaluateJavaScript(string.format("updateContent(%q)", yaml))
end

-- Logic: Save Note
function paperclip.saveNote(content)
    if content == "" or not content:match("%-%-%-.-%-%-%-") then
        hs.alert.show("Error: Empty or Invalid Note")
        return
    end

    local filename = os.date("%Y%m%d-%H%M%S") .. "-pc.md"
    local path = paperclip.destination_dir .. filename
    local file = io.open(path, "w")
    if file then
        file:write(content)
        file:close()
        hs.notify.new({title="Paperclip", informativeText="Note saved: " .. filename}):send()
        paperclip.hide()
    else
        hs.alert.show("Error saving file")
    end
end

-- UI Lifecycle
function paperclip.show()
    paperclip.captureContext()
    local screen = hs.screen.mainScreen()
    local frame = screen:frame()
    paperclip.webview:frame({
        x = frame.x + (frame.w - paperclip.width) / 2,
        y = frame.y + (frame.h - paperclip.height) / 2,
        w = paperclip.width,
        h = paperclip.height
    })
    paperclip.webview:show()
    paperclip.populateYAML("")
    paperclip.is_visible = true
end

-- Force hide
function paperclip.hide()
    paperclip.webview:hide()
    paperclip.is_visible = false
end

function paperclip.toggle()
    if paperclip.is_visible then
        paperclip.hide()
    else
        paperclip.show()
    end
end

-- Global Hotkey
hs.hotkey.bind(paperclip.hotkey[1], paperclip.hotkey[2], paperclip.hotkey[3], function()
    paperclip.toggle()
end)

return paperclip

