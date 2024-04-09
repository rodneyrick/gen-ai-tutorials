#!/bin/bash

# Lista de extensões a serem instaladas
EXTENSIONS=(
    "Gruntfuggly.todo-tree"
    "yy0931.save-as-root"
    "humao.rest-client"
    "mhutchie.git-graph"
    "mohsen1.prettify-json"
    "ms-python.python"
    "ms-python.vscode-pylance"
    "ms-toolsai.datawrangler"
    "ms-toolsai.jupyter-keymap"
    "ms-toolsai.jupyter"
    "ms-vscode.sublime-keybindings"
    "njpwerner.autodocstring"
    "redhat.vscode-yaml"
    "vscode-icons-team.vscode-icons"
)

VSCODE_SERVER_ID=$(ls ~/.vscode-server/bin)

for EXTENSION in "${EXTENSIONS[@]}"; do 
    echo "Install Extension: $EXTENSION"
    ~/.vscode-server/bin/"$VSCODE_SERVER_ID"/bin/code-server --install-extension $EXTENSION
done