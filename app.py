import os
import json
from flask import Flask, request, jsonify, make_response

# --------------------------------------------------------------------------------
# 1) Create the Flask app
# --------------------------------------------------------------------------------
app = Flask(__name__)

# --------------------------------------------------------------------------------
# 2) Serve a single HTML file for the front-end
# --------------------------------------------------------------------------------
@app.route("/")
def index():
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8" />
    <title>Repo Viewer with Change Detection</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background: #f8f9fa;
        }
        h1 {
            color: #333;
        }
        #controls {
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        #folderPath {
            flex: 1;
            padding: 6px;
        }
        button {
            cursor: pointer;
            border: none;
            background-color: #007bff;
            color: #fff;
            padding: 8px 14px;
            border-radius: 4px;
        }
        button:hover {
            background-color: #0069d9;
        }
        #fileTreeWrapper {
            display: flex;
            gap: 20px;
        }
        #fileTree {
            border: 1px solid #ccc;
            padding: 10px;
            width: 320px;
            min-height: 300px;
            overflow-y: auto;
            background: #fff;
        }
        #selectedFilesContainer {
            flex: 1;
        }
        #selectedFilesContent {
            width: 100%;
            height: 300px;
            box-sizing: border-box;
            padding: 10px;
            border: 1px solid #ccc;
            background: #fff;
        }
        .folder {
            font-weight: bold;
            margin-top: 10px;
        }
        .children {
            margin-left: 20px;
        }
        .checkbox-file {
            margin-right: 5px;
        }
        .expanded:before {
            content: "▼ ";
        }
        .collapsed:before {
            content: "▶ ";
        }
        .folder-name {
            cursor: pointer;
        }
        /* Change detection notice */
        #changeNotice {
            display: none;
            background-color: #fff3cd;
            border: 1px solid #ffeeba;
            padding: 10px;
            margin-bottom: 10px;
            border-radius: 4px;
            color: #856404;
        }
        #reflectBtn {
            background-color: #28a745;
        }
        #reflectBtn:hover {
            background-color: #218838;
        }
    </style>
</head>
<body>

<h1>Simple Repo Viewer</h1>

<div id="controls">
    <label for="folderPath">Folder path:</label>
    <input type="text" id="folderPath" size="50" placeholder="e.g. C:/path/to/repo or /home/user/repo" />
    <button id="loadBtn">Load Folder</button>
</div>

<div id="changeNotice">
    <strong>Changes detected in the folder structure!</strong>
    <button id="reflectBtn">Reflect changes</button>
</div>

<div id="fileTreeWrapper">
    <div id="fileTree">Please load a folder...</div>

    <div id="selectedFilesContainer">
        <button id="confirmBtn">Confirm</button>
        <br><br>
        <textarea id="selectedFilesContent" readonly></textarea>
    </div>
</div>

<script>
    // --------------------------------------------------------------------------------
    // Global variables (in the browser) to track current tree and selected files
    // --------------------------------------------------------------------------------
    let currentFolderPath = "";
    let currentTree = null;         // Will store the latest folder tree structure
    let selectedFilesSet = new Set(); 
    let pollInterval = null;        // Will store reference to our polling interval

    // --------------------------------------------------------------------------------
    // Helper to compare two trees (as JSON strings) to detect any difference
    // --------------------------------------------------------------------------------
    function treesAreDifferent(tree1, tree2) {
        // Quick string comparison to detect changes
        return JSON.stringify(tree1) !== JSON.stringify(tree2);
    }

    // --------------------------------------------------------------------------------
    // Polling function: re-fetch tree and compare with currentTree
    // --------------------------------------------------------------------------------
    function checkForFolderChanges() {
        if (!currentFolderPath) return; // No folder loaded, do nothing

        // Send request to build file tree
        fetch("/list_files", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ folder: currentFolderPath })
        })
        .then(res => res.json())
        .then(newTree => {
            if (treesAreDifferent(currentTree, newTree)) {
                // Show the change notice
                document.getElementById("changeNotice").style.display = "block";
            }
        })
        .catch(err => console.error(err));
    }

    // --------------------------------------------------------------------------------
    // Function to build the tree HTML recursively
    // --------------------------------------------------------------------------------
    function createTreeHtml(node) {
        if (node.type === "directory") {
            // Folder
            const folderDiv = document.createElement("div");
            folderDiv.classList.add("folder", "collapsed");

            // Folder name (click to expand/collapse)
            const folderNameSpan = document.createElement("span");
            folderNameSpan.classList.add("folder-name");
            folderNameSpan.textContent = node.name;
            folderNameSpan.onclick = function() {
                if (folderDiv.classList.contains("collapsed")) {
                    folderDiv.classList.remove("collapsed");
                    folderDiv.classList.add("expanded");
                    childrenContainer.style.display = "block";
                } else {
                    folderDiv.classList.remove("expanded");
                    folderDiv.classList.add("collapsed");
                    childrenContainer.style.display = "none";
                }
            };
            folderDiv.appendChild(folderNameSpan);

            // Children
            const childrenContainer = document.createElement("div");
            childrenContainer.classList.add("children");
            childrenContainer.style.display = "none";

            if (node.children && node.children.length > 0) {
                node.children.forEach(child => {
                    childrenContainer.appendChild(createTreeHtml(child));
                });
            }
            folderDiv.appendChild(childrenContainer);
            return folderDiv;
        } else {
            // File
            const fileDiv = document.createElement("div");

            const checkbox = document.createElement("input");
            checkbox.type = "checkbox";
            checkbox.classList.add("checkbox-file");
            checkbox.value = node.path;

            // If previously selected, keep it checked
            if (selectedFilesSet.has(node.path)) {
                checkbox.checked = true;
            }

            // Event to track changes in selection
            checkbox.addEventListener("change", (e) => {
                if (e.target.checked) {
                    selectedFilesSet.add(e.target.value);
                } else {
                    selectedFilesSet.delete(e.target.value);
                }
            });

            const label = document.createElement("label");
            label.textContent = " " + node.name;

            fileDiv.appendChild(checkbox);
            fileDiv.appendChild(label);

            return fileDiv;
        }
    }

    // --------------------------------------------------------------------------------
    // Function to (re)load folder tree
    // --------------------------------------------------------------------------------
    function loadFolder(folderPath) {
        if (!folderPath) {
            alert("Please enter a valid folder path.");
            return;
        }

        const fileTreeDiv = document.getElementById("fileTree");
        fileTreeDiv.innerHTML = "Loading...";

        // Send request to build file tree
        fetch("/list_files", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ folder: folderPath })
        })
        .then(res => res.json())
        .then(data => {
            // Store the new tree
            currentTree = data;
            currentFolderPath = folderPath;

            // Hide the change notice (since we've just refreshed)
            document.getElementById("changeNotice").style.display = "none";

            // Clear out the existing tree UI
            fileTreeDiv.innerHTML = "";

            // Generate new tree UI
            const treeHtml = createTreeHtml(data);
            fileTreeDiv.appendChild(treeHtml);
        })
        .catch(err => {
            console.error(err);
            document.getElementById("fileTree").innerHTML = "Error loading folder structure.";
        });
    }

    // --------------------------------------------------------------------------------
    // On DOM ready, set up event handlers
    // --------------------------------------------------------------------------------
    document.addEventListener("DOMContentLoaded", () => {
        const loadBtn = document.getElementById("loadBtn");
        const folderPathInput = document.getElementById("folderPath");
        const confirmBtn = document.getElementById("confirmBtn");
        const outputArea = document.getElementById("selectedFilesContent");
        const reflectBtn = document.getElementById("reflectBtn");

        // Load folder button click
        loadBtn.onclick = function() {
            selectedFilesSet.clear(); // Reset selection when loading a new folder
            loadFolder(folderPathInput.value.trim());

            // If there's an existing poll, clear it before starting a new one
            if (pollInterval) clearInterval(pollInterval);

            // Start polling every 10 seconds to detect changes
            pollInterval = setInterval(checkForFolderChanges, 10000);
        };

        // Reflect changes button click (re-load the same folder)
        reflectBtn.onclick = function() {
            loadFolder(currentFolderPath);
        };

        // Confirm button click
        confirmBtn.onclick = function() {
            if (selectedFilesSet.size === 0) {
                alert("No files selected.");
                return;
            }

            const filePaths = Array.from(selectedFilesSet);

            fetch("/get_files_content", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ filePaths: filePaths })
            })
            .then(res => res.json())
            .then(data => {
                // data should contain "combinedContent"
                outputArea.value = data.combinedContent;
            })
            .catch(err => {
                console.error(err);
                outputArea.value = "Error retrieving files' content.";
            });
        };
    });
</script>

</body>
</html>
"""
    return make_response(html_content, 200)


# --------------------------------------------------------------------------------
# 3) Endpoint to return a file-tree structure of the folder
# --------------------------------------------------------------------------------
@app.route("/list_files", methods=["POST"])
def list_files():
    data = request.get_json()
    folder = data.get("folder", "")

    # Basic validation
    if not folder or not os.path.isdir(folder):
        return jsonify({"error": "Invalid folder path"}), 400

    def build_tree(path):
        if os.path.isdir(path):
            children = []
            try:
                items = os.listdir(path)
            except Exception:
                items = []

            for item in sorted(items):
                # Skip hidden files/folders if you want
                if item.startswith("."):
                    continue
                full_path = os.path.join(path, item)
                children.append(build_tree(full_path))

            return {
                "name": os.path.basename(path),
                "path": path,
                "type": "directory",
                "children": children
            }
        else:
            return {
                "name": os.path.basename(path),
                "path": path,
                "type": "file"
            }

    tree = build_tree(folder)
    return jsonify(tree)

# --------------------------------------------------------------------------------
# 4) Endpoint to read and combine the content of selected files
# --------------------------------------------------------------------------------
@app.route("/get_files_content", methods=["POST"])
def get_files_content():
    data = request.get_json()
    file_paths = data.get("filePaths", [])

    combined_content = []
    for fpath in file_paths:
        if os.path.isfile(fpath):
            try:
                with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                    # Add file path as a header
                    combined_content.append(f"=== {fpath} ===\n{f.read()}\n\n")
            except Exception as e:
                combined_content.append(f"=== {fpath} ===\nError reading file: {e}\n\n")
        else:
            combined_content.append(f"=== {fpath} ===\n(Not a file or not found)\n\n")

    return jsonify({"combinedContent": "".join(combined_content)})

# --------------------------------------------------------------------------------
# 5) Run the Flask app
# --------------------------------------------------------------------------------
if __name__ == "__main__":
    # Debug=True is optional; you can remove it in production
    app.run(debug=True)
