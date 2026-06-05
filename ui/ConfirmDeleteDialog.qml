import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Dialog {
    id: root
    anchors.centerIn: parent
    width: 400
    modal: true
    padding: 5

    property string message: ""
    property string fontName: ""
    property bool confirmed: false

    background: Rectangle { anchors.fill: parent; color: "#AAAAAA"; border.color: "white"; border.width: 2 }
    
    header: Rectangle {
        height: 30; color: "#0000AA"
        Text { 
            text: "CONFIRM.EXE"
            color: "white"
            anchors.centerIn: parent
            font.family: root.fontName
            renderType: "QtRendering" 
        }
    }
    
    contentItem: Text {
        text: root.message
        color: "black"; font.family: root.fontName; horizontalAlignment: Text.AlignHCenter; renderType: "QtRendering"
        wrapMode: Text.WordWrap
        topPadding: 20
    }
    
    footer: RowLayout {
        Button {
            text: "[ YES ]"
            Layout.fillWidth: true
            onClicked: {
                root.confirmed = true
                root.close()
            }
            background: Rectangle { color: "#AAAAAA" }
            contentItem: Text { text: parent.text; font.family: root.fontName; horizontalAlignment: Text.AlignHCenter; renderType: "QtRendering" }
        }
        Button {
            text: "[ NO ]"
            Layout.fillWidth: true
            onClicked: {
                root.confirmed = false
                root.close()
            }
            background: Rectangle { color: "#AAAAAA" }
            contentItem: Text { text: parent.text; font.family: root.fontName; horizontalAlignment: Text.AlignHCenter; renderType: "QtRendering" }
        }
    }
}