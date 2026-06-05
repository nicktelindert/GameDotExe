import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    id: mainWindow
    visible: true
    width: 900
    height: 700
    title: qsTr("GameDotExe - MS-DOS NOSTALGIA")
    color: "#0000AA" // Classic DOS Blue

    // Load the DOS font from the assets folder
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
                        isIgnored: modelData.isIgnored
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
    AboutDialog {
        id: aboutDialog
        fontName: dosFont.name
    }

    EditGameDialog {
        id: editDialog
        fontName: dosFont.name
    }

    ConfirmDeleteDialog {
        id: confirmDialog
        fontName: dosFont.name
        
        property string folderToDelete: ""
        onClosed: {
            if (confirmed && folderToDelete !== "") {
                bridge.perform_delete_game(folderToDelete)
            }
        }
    }

    // Functies om dialogen te openen
    function openAbout() { aboutDialog.open() }
    function openEdit(gameData) {
        editDialog.openWithData(gameData)
    }
    function openConfirmDelete(gameName, folderName) {
        confirmDialog.message = qsTr("Are you sure you want to delete '%1'?\n\nThis will permanently remove the game from the list and the folder on disk.").arg(gameName)
        confirmDialog.folderToDelete = folderName
        confirmDialog.open()
    }
}