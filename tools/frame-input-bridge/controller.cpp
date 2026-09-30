// MainFrameOS input shortcut service. MIT. No input capture while idle.
#include <QApplication>
#include <QAction>
#include <QDBusConnection>
#include <QDBusMessage>
#include <QDBusPendingCall>
#include <QProcessEnvironment>
#include <QProcess>
#include <QTimer>
#include <QElapsedTimer>
#include <QFile>
#include <QJsonDocument>
#include <QJsonObject>
#include <QDir>
#include <KGlobalAccel>
class Controller : public QObject {
    Q_OBJECT
    Q_CLASSINFO("D-Bus Interface", "org.mainframeos.FrameControl")
    QProcess worker;
    QAction shortcut{this};
    QElapsedTimer debounce;
    QString client,key,target,receiver;
    QByteArray output;
    bool failed=false, stopping=false, captured=false;
    void osd(const QString &text) {
        auto msg=QDBusMessage::createMethodCall("org.kde.plasmashell","/org/kde/osdService","org.kde.osdService","showText");
        msg << "input-keyboard" << text;QDBusConnection::sessionBus().asyncCall(msg);
    }
public:
    explicit Controller(QObject *parent=nullptr):QObject(parent) {
        client=QCoreApplication::applicationDirPath()+"/frame-input-client";
        QFile f(QDir::homePath()+"/.config/mainframeos-frame-control/connection.json");
        if(!f.open(QIODevice::ReadOnly)) qFatal("Missing Frame Control connection configuration");
        auto cfg=QJsonDocument::fromJson(f.readAll()).object();
        key=cfg["identity"].toString();target=cfg["target"].toString();receiver=cfg["receiver"].toString();
        if(key.isEmpty()||target.isEmpty()||receiver.isEmpty())qFatal("Incomplete Frame Control connection configuration");
        shortcut.setObjectName("toggle-frame-control");shortcut.setText("Toggle Steam Frame control");
        KGlobalAccel::self()->setDefaultShortcut(&shortcut,{QKeySequence(Qt::Key_F11)});
        if(!KGlobalAccel::self()->setShortcut(&shortcut,{QKeySequence(Qt::Key_F11)}))qFatal("Could not register Frame Control shortcut");
        connect(&shortcut,&QAction::triggered,this,&Controller::Toggle);
        connect(&worker,&QProcess::readyReadStandardOutput,this,[this]{
            output+=worker.readAllStandardOutput();
            while(output.contains('\n')){
                auto line=output.left(output.indexOf('\n'));output.remove(0,line.size()+1);
                if(line=="ACTIVE")captured=true;
                if(line.startsWith("ERROR:")){failed=true;osd("Frame control unavailable - laptop control restored");}
            }
        });
        connect(&worker,&QProcess::readyReadStandardError,this,[this]{worker.readAllStandardError();});
        connect(&worker,&QProcess::errorOccurred,this,[this](QProcess::ProcessError e){
            if(e==QProcess::FailedToStart){failed=true;osd("Frame control could not start");}
        });
        connect(&worker,qOverload<int,QProcess::ExitStatus>(&QProcess::finished),this,[this](int code,QProcess::ExitStatus){
            if(!failed)osd(code==0||stopping?"Laptop control":"Frame disconnected - laptop control restored");
            stopping=false;captured=false;debounce.restart();
        });
        connect(qApp,&QCoreApplication::aboutToQuit,this,[this]{
            worker.terminate();if(!worker.waitForFinished(1000)){worker.kill();worker.waitForFinished(500);}
        });
    }
public slots:
    void Toggle() {
        if(debounce.isValid()&&debounce.elapsed()<500)return;
        debounce.restart();
        if(worker.state()!=QProcess::NotRunning){
            stopping=true;worker.terminate();
            QTimer::singleShot(1500,this,[this]{if(stopping&&worker.state()!=QProcess::NotRunning)worker.kill();});return;
        }
        failed=false;stopping=false;captured=false;output.clear();
        auto env=QProcessEnvironment::systemEnvironment();env.insert("MAINFRAMEOS_INPUT_OVERLAY","1");
        env.insert("PATH",QCoreApplication::applicationDirPath()+"/transport:"+env.value("PATH"));
        worker.setProcessEnvironment(env);
        worker.start(client,{key,target,receiver});
    }
    QString Status() const {return worker.state()==QProcess::NotRunning?"idle":(captured?"controlling-frame":"connecting");}
};
int main(int argc,char **argv){
    QApplication app(argc,argv);app.setQuitOnLastWindowClosed(false);
    app.setApplicationName("mainframeos-frame-control");app.setApplicationDisplayName("Control Steam Frame");
    Controller control;
    auto bus=QDBusConnection::sessionBus();
    if(!bus.registerObject("/Control",&control,QDBusConnection::ExportAllSlots)||!bus.registerService("org.mainframeos.FrameControl"))return 1;
    return app.exec();
}
#include "controller.moc"
