#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QImage>

namespace Ui {
class MainWindow;
}

class QLabel;
class LeptonThread;
class QGridLayout;

class MainWindow : public QMainWindow
{
    Q_OBJECT

//      enum { ImageWidth = 160, ImageHeight = 120 };
//    enum { ImageWidth = 320, ImageHeight = 240 };
//    enum { ImageWidth = 1024, ImageHeight = 768 };
//    enum { ImageWidth = 800, ImageHeight = 600 };
    enum { ImageWidth = 800, ImageHeight = 480 };

    enum { MAP0 = 0, MAP1 = 1 };

    static int snapshotCount;
    static int colorMapSel;

    QLabel *imageLabel;
    LeptonThread *thread;
    QGridLayout *layout;

    unsigned short rawMin, rawMax;
    QVector<unsigned short> rawData;
    QImage rgbImage;

    private:
    Ui::MainWindow *ui;
    int timerId;

    public:
    explicit MainWindow(QWidget *parent = 0);
    ~MainWindow();

    public slots:
    void saveSnapshot();
    void toggleMap();
    void F1();
    void F2();
    void updateImage(unsigned short *, int, int);

    protected:
        void timerEvent(QTimerEvent *event);
};

#endif // MAINWINDOW_H
