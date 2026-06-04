import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    id: mainWindow
    visible: true
    width: 900
    height: 700
    title: "GameDotExe - MS-DOS NOSTALGIA"
    color: "#0000AA" // Classic DOS Blue

    // Laad het DOS lettertype vanuit de assets map
    FontLoader {
        id: dosFont
        source: "file://" + applicationBasePath + "/assets/font.ttf"
    }

    font.family: dosFont.name

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 15

        // --- Top Bar (Pixel Border Style) ---
        Rectangle {
            Layout.fillWidth: true
            height: 60
            color: "#AAAAAA"
            border.color: "white"
            border.width: 2

            RowLayout {
                anchors.fill: parent
                anchors.margins: 5
                
                TextField {
                    id: searchField
                    placeholderText: "SEARCH_GAME.EXE..."
                    Layout.fillWidth: true
                    font.pixelSize: 20
                    renderType: "QtRendering" // Houdt pixels scherp
                    color: "white"
                    background: Rectangle { color: "black"; border.color: "#55FFFF" }
                    onTextChanged: bridge.filter_games(text)
                }

                Button {
                    text: "[ ISO INSTALL ]"
                    onClicked: bridge.start_iso_install()
                    contentItem: Text {
                        text: parent.text
                        font.family: dosFont.name
                        font.pixelSize: 16
                        font.bold: true
                        color: "black"
                        horizontalAlignment: Text.AlignHCenter
                    }
                    background: Rectangle { 
                        color: parent.pressed ? "#55FFFF" : "#AAAAAA"
                        border.color: "black"
                    }
                }

                Button {
                    text: "[ SCAN ]"
                    onClicked: bridge.force_scan()
                    contentItem: Text {
                        text: parent.text
                        font.family: dosFont.name
                        font.pixelSize: 16
                        font.bold: true
                        color: "black"
                        horizontalAlignment: Text.AlignHCenter
                    }
                    background: Rectangle { 
                        color: parent.pressed ? "#55FFFF" : "#AAAAAA"
                        border.color: "black"
                    }
                }

                Button {
                    text: "[ ABOUT ]"
                    onClicked: openAbout()
                    contentItem: Text {
                        text: parent.text
                        font.family: dosFont.name
                        font.pixelSize: 16
                        font.bold: true
                        color: "black"
                        horizontalAlignment: Text.AlignHCenter
                    }
                    background: Rectangle { 
                        color: parent.pressed ? "#55FFFF" : "#AAAAAA"
                        border.color: "black"
                    }
                }
            }
        }

        // --- Game Grid ---
        Item {
            Layout.fillWidth: true
            Layout.fillHeight: true

            GridView {
                id: gameGrid
                anchors.fill: parent
                cellWidth: 210
                cellHeight: 270
                model: bridge ? bridge.games : []
                clip: true

                delegate: Item {
                    width: 210
                    height: 270
                    GameWidget {
                        anchors.centerIn: parent
                        name: modelData.name
                        icon: modelData.icon
                        releaseDate: "Released: " + modelData.releaseDate
                        command: modelData.command
                        gameModelData: modelData
                        isSelected: GridView.isCurrentItem
                        onClicked: gameGrid.currentIndex = index
                    }
                }
            }

        }

        // --- Status Bar ---
        Rectangle {
            Layout.fillWidth: true
            height: 25
            color: "#AAAAAA"
            Row {
                anchors.verticalCenter: parent.verticalCenter
                x: 5
                Text { text: " C:\\> "; font.bold: true; font.family: dosFont.name; font.pixelSize: 14; renderType: "QtRendering" }
                Text {
                    id: cursor
                    text: "_"
                    font.bold: true
                    font.family: dosFont.name
                    font.pixelSize: 14
                    renderType: "QtRendering"
                    Timer {
                        interval: 500; running: true; repeat: true
                        onTriggered: cursor.visible = !cursor.visible
                    }
                }
            }
        }
    }

    // --- Custom QML Dialogs (DOS Style) ---

    // About Dialog
    Dialog {
        id: aboutDialog
        anchors.centerIn: parent
        width: 400
        modal: true
        background: Rectangle { color: "#AAAAAA"; border.color: "white"; border.width: 2 }
        header: Rectangle { 
            height: 30; color: "#0000AA"
            Text { text: "ABOUT.EXE"; color: "white"; anchors.centerIn: parent; font.family: dosFont.name }
        }
        contentItem: Text {
            text: "GAMEDOTEXE v1.0\n\nA modern DOSBox launcher\nbuilt for nostalgia.\n\n(C) 2024 Nick"
            color: "black"; font.family: dosFont.name; horizontalAlignment: Text.AlignHCenter
            topPadding: 20
        }
        footer: Button {
            text: "[ OK ]"
            onClicked: aboutDialog.close()
            background: Rectangle { color: "#AAAAAA" }
            contentItem: Text { text: parent.text; font.family: dosFont.name; horizontalAlignment: Text.AlignHCenter }
        }
    }

    // Edit Dialog
    Dialog {
        id: editDialog
        anchors.centerIn: parent
        width: 600
        height: 650
        modal: true
        padding: 5
        property var currentGame: ({})
        // De achtergrondrechthoek moet de dialoog vullen om de rand correct weer te geven
        background: Rectangle { anchors.fill: parent; color: "#AAAAAA"; border.color: "white"; border.width: 2 }
        header: Rectangle { 
            height: 30; color: "#0000AA"
            Text { text: "EDIT_CONFIG.SYS"; color: "white"; anchors.centerIn: parent; font.family: dosFont.name; renderType: "QtRendering" }
        }

        contentItem: ScrollView {
            id: editScroll
            clip: true
            contentWidth: -1 // Disable horizontal scroll
            
            ColumnLayout {
                width: editDialog.width - 40
                spacing: 15
                
                ColumnLayout {
                    Layout.fillWidth: true
                    Text { text: "DISPLAY NAME:"; font.family: dosFont.name; renderType: "QtRendering" }
                    TextField {
                        id: editNameInput
                        Layout.fillWidth: true
                        background: Rectangle { color: "black"; border.color: "white" }
                        color: "white"; font.family: dosFont.name; renderType: "QtRendering"
                    }
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    Text { text: "EXECUTABLE (RELATIVE):"; font.family: dosFont.name; renderType: "QtRendering" }
                    RowLayout {
                        TextField {
                            id: editExecInput
                            Layout.fillWidth: true
                            background: Rectangle { color: "black"; border.color: "white" }
                            color: "white"; font.family: dosFont.name; renderType: "QtRendering"
                        }
                        Button {
                            text: "..."
                            width: 30
                            onClicked: {
                                let res = bridge.browse_executable(editDialog.currentGame.folder)
                                if (res !== "") editExecInput.text = res
                            }
                        }
                    }
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    Text { text: "SETUP (RELATIVE):"; font.family: dosFont.name; renderType: "QtRendering" }
                    RowLayout {
                        TextField {
                            id: editSetupInput
                            Layout.fillWidth: true
                            background: Rectangle { color: "black"; border.color: "white" }
                            color: "white"; font.family: dosFont.name; renderType: "QtRendering"
                        }
                        Button {
                            text: "..."
                            width: 30
                            onClicked: {
                                let res = bridge.browse_executable(editDialog.currentGame.folder)
                                if (res !== "") editSetupInput.text = res
                            }
                        }
                    }
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    Text { text: "ARTWORK PATH:"; font.family: dosFont.name; renderType: "QtRendering" }
                    RowLayout {
                        TextField {
                            id: editIconInput
                            Layout.fillWidth: true
                            background: Rectangle { color: "black"; border.color: "white" }
                            color: "white"; font.family: dosFont.name; renderType: "QtRendering"
                        }
                        Button {
                            text: "..."
                            width: 30
                            onClicked: {
                                let res = bridge.browse_image()
                                if (res !== "") editIconInput.text = res
                            }
                        }
                    }
                }

                RowLayout {
                    Layout.fillWidth: true
                    ColumnLayout {
                        Layout.fillWidth: true
                        Text { text: "RELEASE DATE:"; font.family: dosFont.name; renderType: "QtRendering" }
                        TextField {
                            id: editDateInput
                            Layout.fillWidth: true
                            background: Rectangle { color: "black"; border.color: "white" }
                            color: "white"; font.family: dosFont.name; renderType: "QtRendering"
                        }
                    }
                    ColumnLayout {
                        Layout.fillWidth: true
                        Text { text: "COMPATIBILITY:"; font.family: dosFont.name; renderType: "QtRendering" }
                        TextField {
                            id: editCompInput
                            Layout.fillWidth: true
                            background: Rectangle { color: "black"; border.color: "white" }
                            color: "white"; font.family: dosFont.name; renderType: "QtRendering"
                        }
                    }
                }
            }
        }

        footer: RowLayout {
            Button {
                text: "[ SAVE ]"
                Layout.fillWidth: true
                onClicked: {
                    let data = {
                        "folder": editDialog.currentGame.folder,
                        "name": editNameInput.text,
                        "command": editDialog.currentGame.command,
                        "internal_exec": editExecInput.text,
                        "internal_setup": editSetupInput.text,
                        "compatibility": editCompInput.text,
                        "releaseDate": editDateInput.text,
                        "icon_path": editIconInput.text,
                        "iso_path": editDialog.currentGame.iso_path
                    }
                    bridge.show_edit_game_dialog(data)
                    editDialog.close()
                }
                background: Rectangle { color: "#AAAAAA" }
                contentItem: Text { text: parent.text; font.family: dosFont.name; horizontalAlignment: Text.AlignHCenter; renderType: "QtRendering" }
            }
            Button {
                text: "[ CANCEL ]"
                Layout.fillWidth: true
                onClicked: editDialog.close()
                background: Rectangle { color: "#AAAAAA" }
                contentItem: Text { text: parent.text; font.family: dosFont.name; horizontalAlignment: Text.AlignHCenter; renderType: "QtRendering" }
            }
        }
    }

    // Bevestigingsdialoog (voor Verwijderen)
    Dialog {
        id: confirmDialog
        anchors.centerIn: parent
        width: 400
        modal: true
        property string message: ""
        padding: 5
        property bool confirmed: false // Deze property wordt ingesteld door de knoppen

        background: Rectangle { anchors.fill: parent; color: "#AAAAAA"; border.color: "white"; border.width: 2 }
        header: Rectangle {
            height: 30; color: "#0000AA"
            Text { text: "CONFIRM.EXE"; color: "white"; anchors.centerIn: parent; font.family: dosFont.name; renderType: "QtRendering" }
        }
        contentItem: Text {
            text: confirmDialog.message
            color: "black"; font.family: dosFont.name; horizontalAlignment: Text.AlignHCenter; renderType: "QtRendering"
            wrapMode: Text.WordWrap
            topPadding: 20
        }
        footer: RowLayout {
            Button {
                text: "[ YES ]"
                Layout.fillWidth: true
                onClicked: {
                    confirmDialog.confirmed = true
                    confirmDialog.close()
                }
                background: Rectangle { color: "#AAAAAA" }
                contentItem: Text { text: parent.text; font.family: dosFont.name; horizontalAlignment: Text.AlignHCenter; renderType: "QtRendering" }
            }
            Button {
                text: "[ NO ]"
                Layout.fillWidth: true
                onClicked: {
                    confirmDialog.confirmed = false
                    confirmDialog.close()
                }
                background: Rectangle { color: "#AAAAAA" }
                contentItem: Text { text: parent.text; font.family: dosFont.name; horizontalAlignment: Text.AlignHCenter; renderType: "QtRendering" }
            }
        }
    }

    // Functies om dialogen te openen
    function openAbout() { aboutDialog.open() }
    function openEdit(gameData) {
        editDialog.currentGame = gameData
        editNameInput.text = gameData.name || ""
        editExecInput.text = gameData.internal_exec || ""
        editSetupInput.text = gameData.internal_setup || ""
        editIconInput.text = gameData.icon_path || ""
        editDateInput.text = gameData.releaseDate || ""
        editCompInput.text = gameData.compatibility || ""
        editDialog.open()
    }
    function openConfirmDelete(gameName, folderName) {
        confirmDialog.message = "Weet je zeker dat je '" + gameName + "' wilt verwijderen?\n\nDit zal de game permanent verwijderen uit de lijst en de map op schijf."
        confirmDialog.open()
        confirmDialog.closed.connect(function() {
            if (confirmDialog.confirmed) {
                bridge.perform_delete_game(folderName)
            }
        })
    }
}