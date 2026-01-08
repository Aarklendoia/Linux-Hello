import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import org.kde.kirigami 2.13 as Kirigami

Kirigami.Page {
    id: enrollPage
    title: "Enregistrement"
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Kirigami.Units.largeSpacing * 1.5
        spacing: Kirigami.Units.largeSpacing
        
        // Titre
        Label {
            text: "Enregistrer un nouveau visage"
            font.pixelSize: 20
            font.weight: Font.Bold
            color: Kirigami.Theme.textColor
        }
        
        // Zone de préview
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 300
            color: Kirigami.Theme.backgroundColor
            border.color: Kirigami.Theme.textColor
            border.width: 1
            
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: Kirigami.Units.mediumSpacing
                spacing: Kirigami.Units.mediumSpacing
                
                Label {
                    text: "Aperçu de la caméra"
                    color: Kirigami.Theme.disabledTextColor
                    Layout.alignment: Qt.AlignHCenter
                    Layout.fillHeight: true
                    Layout.fillWidth: true
                    verticalAlignment: Text.AlignVCenter
                    horizontalAlignment: Text.AlignHCenter
                }
            }
        }
        
        // Barre de progression
        ColumnLayout {
            spacing: Kirigami.Units.smallSpacing * 1.5
            Layout.fillWidth: true
            
            Label {
                text: "Progression : 0%"
                color: Kirigami.Theme.textColor
                id: progressLabel
            }
            
            ProgressBar {
                value: 0
                Layout.fillWidth: true
                id: progressBar
            }
        }
        
        // Instructions
        Label {
            text: "Présentez votre visage à la caméra. Le système capturera plusieurs angles pour une meilleure reconnaissance."
            wrapMode: Text.WordWrap
            color: Kirigami.Theme.disabledTextColor
            Layout.fillWidth: true
        }
        
        // Espace flexible
        Item { Layout.fillHeight: true }
        
        // Boutons d'action
        RowLayout {
            spacing: Kirigami.Units.mediumSpacing * 1.5
            Layout.fillWidth: true
            
            Button {
                text: "Démarrer la capture"
                Layout.fillWidth: true
                implicitHeight: Kirigami.Units.gridUnit * 2.2
                enabled: !linuxHelloApp.capturing
                
                palette.buttonText: Kirigami.Theme.highlightedTextColor
                palette.button: Kirigami.Theme.highlightColor
                
                onClicked: {
                    mainWindow.startCapture()
                }
            }
            
            Button {
                text: "Arrêter"
                Layout.fillWidth: true
                implicitHeight: Kirigami.Units.gridUnit * 2.2
                enabled: linuxHelloApp.capturing
                onClicked: {
                    mainWindow.stopCapture()
                }
            }
            
            Button {
                text: "Annuler"
                Layout.fillWidth: true
                implicitHeight: Kirigami.Units.gridUnit * 2.2
                onClicked: {
                    mainWindow.navigateToHome()
                }
            }
        }
    }
    
    // Connexions aux signaux de l'app
    Connections {
        target: mainWindow
        
        function onAppProgressChanged(value) {
            progressBar.value = value / 100.0
            progressLabel.text = "Progression : " + value + "%"
        }
        
        function onCaptureCompletedSignal() {
            progressBar.value = 1.0
            progressLabel.text = "Progression : 100%"
        }
    }
}
