#include <QGuiApplication>
#include <QQmlApplicationEngine>
#include <QIcon>
#include <QStandardPaths>
#include <QString>
#include <QDir>

int main(int argc, char *argv[])
{
    QGuiApplication app(argc, argv);

    // Définir l'icône de la barre de titre et du système
    app.setWindowIcon(QIcon("/usr/share/icons/hicolor/scalable/apps/linux-hello.svg"));

    // Déterminer le chemin du fichier QML
    QString qmlPath;
    
    // Vérifier d'abord l'installation système
    if (QDir("/usr/share/linux-hello/qml-modules/Linux/Hello").exists()) {
        qmlPath = "qrc:/Linux/Hello/main.qml";
    } else {
        // Sinon utiliser le chemin de développement
        QString appDir = QCoreApplication::applicationDirPath();
        qmlPath = appDir + "/../qml/main.qml";
    }

    QQmlApplicationEngine engine;

    // Configurer les chemins d'import QML
    engine.addImportPath("/usr/share/linux-hello/qml-modules");
    engine.addImportPath("/usr/lib/x86_64-linux-gnu/qt6/qml");
    engine.addImportPath("/usr/lib/qt6/qml");

    const QUrl url(QStringLiteral("file:///usr/share/linux-hello/qml-modules/Linux/Hello/main.qml"));
    engine.load(url);

    if (engine.rootObjects().isEmpty())
        return -1;

    return app.exec();
}
