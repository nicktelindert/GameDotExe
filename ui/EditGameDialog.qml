import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Dialog {
    id: root
    anchors.centerIn: parent
    width: 600
    height: 650
    modal: true
    padding: 5

    property var currentGame: ({})
    property string fontName: ""

    background: Rectangle { anchors.fill: parent; color: "#AAAAAA"; border.color: "white"; border.width: 2 }
    
    header: Rectangle { 
        height: 30; color: "#0000AA"
        Text { 
            text: "EDIT_CONFIG.SYS"
            color: "white"
            anchors.centerIn: parent
            font.family: root.fontName
            renderType: "QtRendering" 
        }
    }

    function openWithData(gameData) {
        currentGame = gameData
        editNameInput.text = gameData.name || ""
        editExecInput.text = gameData.internal_exec || ""
        editSetupInput.text = gameData.internal_setup || ""
        editIconInput.text = gameData.icon_path || ""
        editDateInput.text = gameData.releaseDate || ""
        editCompInput.text = gameData.compatibility || ""
        root.open()
    }

    contentItem: ScrollView {
        clip: true
        contentWidth: -1 
        
        ColumnLayout {
            width: root.width - 40
            spacing: 15
            
            ColumnLayout {
                Layout.fillWidth: true
                Text { text: "DISPLAY NAME:"; font.family: root.fontName; renderType: "QtRendering" }
                TextField {
                    id: editNameInput
                    Layout.fillWidth: true
                    background: Rectangle { color: "black"; border.color: "white" }
                    color: "white"; font.family: root.fontName; renderType: "QtRendering"
                }
            }

            ColumnLayout {
                Layout.fillWidth: true
                Text { text: "EXECUTABLE (RELATIVE):"; font.family: root.fontName; renderType: "QtRendering" }
                RowLayout {
                    TextField {
                        id: editExecInput
                        Layout.fillWidth: true
                        background: Rectangle { color: "black"; border.color: "white" }
                        color: "white"; font.family: root.fontName; renderType: "QtRendering"
                    }
                    Button {
                        text: "..."
                        width: 30
                        onClicked: {
                            let res = bridge.browse_executable(root.currentGame.folder)
                            if (res !== "") editExecInput.text = res
                        }
                    }
                }
            }

            ColumnLayout {
                Layout.fillWidth: true
                Text { text: "SETUP (RELATIVE):"; font.family: root.fontName; renderType: "QtRendering" }
                RowLayout {
                    TextField {
                        id: editSetupInput
                        Layout.fillWidth: true
                        background: Rectangle { color: "black"; border.color: "white" }
                        color: "white"; font.family: root.fontName; renderType: "QtRendering"
                    }
                    Button {
                        text: "..."
                        width: 30
                        onClicked: {
                            let res = bridge.browse_executable(root.currentGame.folder)
                            if (res !== "") editSetupInput.text = res
                        }
                    }
                }
            }

            ColumnLayout {
                Layout.fillWidth: true
                Text { text: "ARTWORK PATH:"; font.family: root.fontName; renderType: "QtRendering" }
                RowLayout {
                    TextField {
                        id: editIconInput
                        Layout.fillWidth: true
                        background: Rectangle { color: "black"; border.color: "white" }
                        color: "white"; font.family: root.fontName; renderType: "QtRendering"
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
                    Text { text: "RELEASE DATE:"; font.family: root.fontName; renderType: "QtRendering" }
                    TextField {
                        id: editDateInput
                        Layout.fillWidth: true
                        background: Rectangle { color: "black"; border.color: "white" }
                        color: "white"; font.family: root.fontName; renderType: "QtRendering"
                    }
                }
                ColumnLayout {
                    Layout.fillWidth: true
                    Text { text: "COMPATIBILITY:"; font.family: root.fontName; renderType: "QtRendering" }
                    TextField {
                        id: editCompInput
                        Layout.fillWidth: true
                        background: Rectangle { color: "black"; border.color: "white" }
                        color: "white"; font.family: root.fontName; renderType: "QtRendering"
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
                    "folder": root.currentGame.folder,
                    "name": editNameInput.text,
                    "command": root.currentGame.command,
                    "internal_exec": editExecInput.text,
                    "internal_setup": editSetupInput.text,
                    "compatibility": editCompInput.text,
                    "releaseDate": editDateInput.text,
                    "icon_path": editIconInput.text,
                    "iso_path": root.currentGame.iso_path
                }
                bridge.show_edit_game_dialog(data)
                root.close()
            }
            background: Rectangle { color: "#AAAAAA" }
            contentItem: Text { text: parent.text; font.family: root.fontName; horizontalAlignment: Text.AlignHCenter; renderType: "QtRendering" }
        }
        Button {
            text: "[ CANCEL ]"
            Layout.fillWidth: true
            onClicked: root.close()
            background: Rectangle { color: "#AAAAAA" }
            contentItem: Text { text: parent.text; font.family: root.fontName; horizontalAlignment: Text.AlignHCenter; renderType: "QtRendering" }
        }
    }
}