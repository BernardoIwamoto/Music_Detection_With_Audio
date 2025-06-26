import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel,
    QFileDialog, QVBoxLayout, QMessageBox
)
from structure import OrganizadorMusical

caminho_data = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))

organizador = OrganizadorMusical(caminho_data)


class AppInterface(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Organizador de Músicas")
        self.setGeometry(100, 100, 400, 250)
        self.organizador = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.label_status = QLabel("Selecione uma pasta com músicas .wav")
        layout.addWidget(self.label_status)

        btn_selecionar_pasta = QPushButton("Selecionar Pasta de Músicas")
        btn_selecionar_pasta.clicked.connect(self.selecionar_pasta)
        layout.addWidget(btn_selecionar_pasta)

        btn_mapa = QPushButton("Mostrar Mapa de Estilos")
        btn_mapa.clicked.connect(self.mostrar_mapa)
        layout.addWidget(btn_mapa)

        btn_nova = QPushButton("Analisar Nova Música")
        btn_nova.clicked.connect(self.analisar_nova)
        layout.addWidget(btn_nova)

        self.setLayout(layout)

    def selecionar_pasta(self):
        pasta = QFileDialog.getExistingDirectory(self, "Selecione a pasta com músicas")
        if pasta:
            self.label_status.setText("Carregando músicas...")
            QApplication.processEvents()
            try:
                self.organizador = OrganizadorMusical(pasta)
                self.label_status.setText("Músicas carregadas com sucesso!")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao carregar músicas:\n{str(e)}")

    def mostrar_mapa(self):
        if self.organizador:
            self.organizador.mostrar_mapa()
        else:
            QMessageBox.information(self, "Aviso", "Por favor, carregue uma pasta primeiro.")

    def analisar_nova(self):
        if not self.organizador:
            QMessageBox.warning(self, "Atenção", "Carregue uma pasta de músicas primeiro.")
            return

        caminho, _ = QFileDialog.getOpenFileName(self, "Selecione a nova música", filter="Áudio (*.wav)")
        if caminho and caminho.endswith(".wav"):
            try:
                self.organizador.sugerir_musicas_parecidas(caminho)
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao analisar a música:\n{str(e)}")
        else:
            QMessageBox.information(self, "Arquivo inválido", "Por favor, selecione um arquivo .wav válido.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = AppInterface()
    janela.show()
    sys.exit(app.exec_())
