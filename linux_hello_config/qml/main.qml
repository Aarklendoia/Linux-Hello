import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Window 2.15
import org.kde.kirigami 2.13 as Kirigami

Kirigami.ApplicationWindow {
    id: mainWindow
    title: "Linux Hello - Configuration"
    width: 800
    height: 600
    visible: true
    
    // Thème Breeze automatique via Kirigami
    color: Kirigami.Theme.backgroundColor
    
    // Stack de pages pour navigation
    pageStack.initialPage: homeComponent
    
    // Propriétés globales de l'app
    QtObject {
        id: appController
        
        // État de l'application
        property bool capturing: false
        property int progress: 0
        property var facesList: [
            { name: "Visage 1", confidence: 92, date: "2026-01-08" },
            { name: "Visage 2", confidence: 88, date: "2026-01-07" }
        ]
        
        // Signaux
        signal appProgressChanged(int value)
        signal captureCompletedSignal()
        signal captureErrorSignal(string message)
        signal navigateToHomeSignal()
        signal navigateToEnrollSignal()
        signal navigateToSettingsSignal()
        signal navigateToManageFacesSignal()
        
        // Méthodes
        function startCapture() {
            capturing = true
            progress = 0
            // TODO: Appel D-Bus vers hello_daemon
            animateProgress()
        }
        
        function stopCapture() {
            capturing = false
            // TODO: Signal D-Bus
        }
        
        function saveSettings() {
            // TODO: Sauvegarder via D-Bus
            console.log("Paramètres sauvegardés")
        }
        
        function deleteFace(index) {
            facesList.splice(index, 1)
            // TODO: Appel D-Bus
            facesList = facesList  // Trigger update
        }
        
        function navigateToHomeImpl() {
            mainWindow.pageStack.clear()
            mainWindow.pageStack.push(homeComponent)
        }
        
        function navigateToEnrollImpl() {
            mainWindow.pageStack.push(enrollComponent)
        }
        
        function navigateToSettingsImpl() {
            mainWindow.pageStack.push(settingsComponent)
        }
        
        function navigateToManageFacesImpl() {
            mainWindow.pageStack.push(manageFacesComponent)
        }
        
        function animateProgress() {
            if (capturing && progress < 100) {
                progress += Math.random() * 15
                if (progress > 100) progress = 100
                appProgressChanged(progress)
                if (progress >= 100) {
                    capturing = false
                    captureCompletedSignal()
                } else {
                    progressTimer.restart()
                }
            }
        }
    }
    
    Timer {
        id: progressTimer
        interval: 500
        onTriggered: appController.animateProgress()
    }
    
    // Raccourcis globaux
    function startCapture() { appController.startCapture() }
    function stopCapture() { appController.stopCapture() }
    function saveSettings() { appController.saveSettings() }
    function deleteFace(index) { appController.deleteFace(index) }
    function navigateToHome() { appController.navigateToHomeImpl() }
    function navigateToEnroll() { appController.navigateToEnrollImpl() }
    function navigateToSettings() { appController.navigateToSettingsImpl() }
    function navigateToManageFaces() { appController.navigateToManageFacesImpl() }
    
    // Page d'accueil
    Component {
        id: homeComponent
        Home { }
    }
    
    // Page d'enregistrement
    Component {
        id: enrollComponent
        Enrollment { }
    }
    
    // Page de paramètres
    Component {
        id: settingsComponent
        Settings { }
    }
    
    // Page de gestion des visages
    Component {
        id: manageFacesComponent
        ManageFaces { }
    }
}
