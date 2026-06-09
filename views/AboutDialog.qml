import QtQuick
import QtQuick.Controls

Dialog {
    id: root
    anchors.centerIn: parent
    width: 400
    modal: true
    
    property string fontName: ""

    background: Rectangle { color: "#AAAAAA"; border.color: "white"; border.width: 2 }
    header: Rectangle { 
        height: 30; color: "#0000AA"
        Text { text: "ABOUT.EXE"; color: "white"; anchors.centerIn: parent; font.family: root.fontName }
    }
    contentItem: Text {
        text: "GAMEDOTEXE v1.0\n\nA modern DOSBox launcher\nbuilt for nostalgia.\n\n(C) 2024 Nick"
        color: "black"; font.family: root.fontName; horizontalAlignment: Text.AlignHCenter
        topPadding: 20
    }
    footer: Button {
        text: "[ OK ]"
        onClicked: root.close()
        background: Rectangle { color: "#AAAAAA" }
        contentItem: Text { text: parent.text; font.family: root.fontName; horizontalAlignment: Text.AlignHCenter }
    }
}