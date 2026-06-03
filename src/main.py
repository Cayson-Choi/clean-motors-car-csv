import sys
from PySide6.QtWidgets import QApplication, QFileDialog, QMessageBox
from src.gui.main_window import MainWindow
from src.gui.dedup_window import DedupWindow
from src.gui.style import APP_STYLE
from src import engine

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(APP_STYLE)
    win = MainWindow()
    holder = {}

    def on_processed(header, data, summary, encoding):
        dups = engine.detect_duplicates(data)
        if dups:
            holder['dedup'] = DedupWindow(header, data, summary, encoding)
            holder['dedup'].show()
            win.close()
        else:
            out,_ = QFileDialog.getSaveFileName(win,'최종 CSV 저장','일반정기차량_최종.csv','CSV (*.csv)')
            if out:
                engine.write_csv(out, header, data, encoding)
                QMessageBox.information(win,'완료', f'최종 {len(data)}대 저장 완료\n{out}')

    win.processed.connect(on_processed)
    win.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
