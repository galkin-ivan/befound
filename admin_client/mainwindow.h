#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QTimer>
#include "usertablemodel.h"
#include "settingswindow.h"
#include "globals.h"

namespace Ui {
class MainWindow;
}

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    explicit MainWindow(QWidget *parent = 0);
    ~MainWindow();

public slots:
    void settingsWindowShow();
    void setSettings();
    void sendRequest();
    void updateUsers(QList<Globals::User> users);
    void updateUserTrack(QList<Globals::Coords> track);
    void printInfo(QString msg);
    void selectUser(QModelIndex index);
    void onAuth();
    void onLoggout();

private:
    Ui::MainWindow *ui;

    UserTableModel *m_usersAtTaskModel;
    UserTableModel *m_usersInAlarm;
    SettingsWindow *m_settingsWindow;

    QTimer *m_timer;

    quint64 m_selectedUserID;
};

#endif // MAINWINDOW_H
