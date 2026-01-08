import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import org.kde.kirigami 2.13 as Kirigami

Kirigami.Page {
    id: homePage
    title: "Accueil"
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Kirigami.Units.largeSpacing * 1.5
        spacing: Kirigami.Units.largeSpacing
        
        // Titre principal
        Label {
            text: "Linux Hello"
            font.pixelSize: 32
            font.weight: Font.Bold
            color: Kirigami.Theme.textColor
            Layout.alignment: Qt.AlignHCenter
        }
        
        // Sous-titre
        Label {
            text: "Configuration d'authentification biométrique"
            font.pixelSize: 16
            color: Kirigami.Theme.disabledTextColor
            Layout.alignment: Qt.AlignHCenter
            Layout.fillWidth: true
            wrapMode: Text.WordWrap
            horizontalAlignment: Text.AlignHCenter
        }
        
        // Espace
        Item { Layout.fillHeight: true }
        
        // Contenu principal
        ColumnLayout {
            spacing: Kirigami.Units.mediumSpacing * 1.5
            Layout.alignment: Qt.AlignHCenter
            Layout.fillWidth: true
            Layout.maximumWidth: 400
            
            Label {
                text: "Bienvenue dans Linux Hello, le système d'authentification biométrique pour KDE."
                wrapMode: Text.WordWrap
                color: Kirigami.Theme.textColor
                Layout.fillWidth: true
            }
            
            Label {
                text: "Vous pouvez :"
                font.weight: Font.Bold
                color: Kirigami.Theme.textColor
                Layout.fillWidth: true
            }
            
            ColumnLayout {
                spacing: Kirigami.Units.smallSpacing * 2
                Layout.leftMargin: Kirigami.Units.largeSpacing * 1.5
                
                Label {
                    text: "• Enregistrer votre visage pour l'authentification"
                    color: Kirigami.Theme.textColor
                    wrapMode: Text.WordWrap
                }
                
                Label {
                    text: "• Gérer les visages enregistrés"
                    color: Kirigami.Theme.textColor
                    wrapMode: Text.WordWrap
                }
                
                Label {
                    text: "• Configurer les paramètres de sécurité"
                    color: Kirigami.Theme.textColor
                    wrapMode: Text.WordWrap
                }
            }
        }
        
        // Espace
        Item { Layout.fillHeight: true }
        
        // Boutons de navigation
        ColumnLayout {
            spacing: Kirigami.Units.mediumSpacing * 1.5
            Layout.fillWidth: true
            
            Button {
                text: "📷 Enregistrer un Visage"
                Layout.fillWidth: true
                implicitHeight: Kirigami.Units.gridUnit * 2.5
                onClicked: mainWindow.navigateToEnroll()
                
                palette.buttonText: Kirigami.Theme.highlightedTextColor
                palette.button: Kirigami.Theme.highlightColor
            }
            
            Button {
                text: "👤 Gérer les Visages"
                Layout.fillWidth: true
                implicitHeight: Kirigami.Units.gridUnit * 2.5
                onClicked: mainWindow.navigateToManageFaces()
            }
            
            Button {
                text: "⚙️ Paramètres"
                Layout.fillWidth: true
                implicitHeight: Kirigami.Units.gridUnit * 2.5
                onClicked: mainWindow.navigateToSettings()
            }
        }
    }
}
