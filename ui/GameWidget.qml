import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: root
    width: 200
    height: 260
    color: "#000000"
    border.color: (mouseArea.containsMouse || isSelected) ? "#FFFF55" : "#AAAAAA"
    border.width: mouseArea.containsMouse ? 3 : 1

    property alias name: nameText.text
    property alias icon: gameImage.source
    property alias releaseDate: dateText.text
    property string command: ""
    property bool isSelected: false
    property var gameModelData: ({}) // Om het hele modelData object door te geven voor contextmenu's
    signal clicked()

    Column {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 8

        Image {
            id: gameImage
            width: 160
            height: 120
            fillMode: Image.PreserveAspectFit
            anchors.horizontalCenter: parent.horizontalCenter
            smooth: false // Cruciaal voor de pixel-look
        }

        Text {
            id: nameText
            color: mouseArea.containsMouse ? "#FFFF55" : "white"
            width: parent.width
            wrapMode: Text.WordWrap
            horizontalAlignment: Text.AlignHCenter
            font.pixelSize: 16
            font.bold: true
            renderType: "QtRendering"
        }

        Text {
            id: dateText
            color: "#AAAAAA"
            width: parent.width
            horizontalAlignment: Text.AlignHCenter
            font.pixelSize: 12
            renderType: "QtRendering"
            wrapMode: Text.WordWrap // Zorgt ervoor dat lange datums wrappen
            height: implicitHeight // Laat de hoogte bepalen door de tekstinhoud
        }

        // Een echte DOS "button" look
        Rectangle {
            width: parent.width * 0.8
            height: 30
            anchors.horizontalCenter: parent.horizontalCenter
            color: playMouse.pressed ? "#55FFFF" : "#AAAAAA"
            border.color: "black"
            border.width: 1
            visible: mouseArea.containsMouse

            Text {
                text: "[ PLAY ]"
                anchors.centerIn: parent
                font.family: dosFont.name
                font.pixelSize: 14
                font.bold: true
                color: "black"
            }

            MouseArea {
                id: playMouse
                anchors.fill: parent
                onClicked: bridge.launch_game(root.command)
            }
        }
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        acceptedButtons: Qt.LeftButton | Qt.RightButton
        onClicked: function(mouse) {
            root.clicked()
            if (mouse.button === Qt.RightButton) {
                contextMenu.popup()
            }
        }
    }

    Menu {
        id: contextMenu
        font.family: dosFont.name
        
        MenuItem {
            text: "EDIT PROPERTIES"
            onClicked: mainWindow.openEdit(root.gameModelData)
        }
        MenuItem {
            text: "DELETE GAME"
            onClicked: mainWindow.openConfirmDelete(root.name, root.gameModelData.folder)
        }
    }
}