import sys
import os
import cv2
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QListWidget,
    QFileDialog, QMessageBox, QTabWidget, QVBoxLayout, QHBoxLayout,
    QCheckBox, QSlider, QScrollArea
)
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt, QTimer


class AbaGerir(QWidget):
    def __init__(self):
        super().__init__()
        self.lista_fotos = []
        self.foto_temporaria = None
        self.modo_foto = False

        self.initUI()
        self.webcam = cv2.VideoCapture(0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.atualizar_frame)
        self.timer.start(30)

    def initUI(self):
        layout = QHBoxLayout()

        # Área de vídeo
        self.area_video = QLabel("Webcam")
        self.area_video.setFixedSize(500, 350)
        self.area_video.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Botões principais
        self.btn_capturar = QPushButton("Capturar")
        self.btn_capturar.clicked.connect(self.tirar_foto)

        self.btn_guardar = QPushButton("Guardar imagem")
        self.btn_guardar.clicked.connect(self.guardar_foto)
        self.btn_guardar.hide()

        self.btn_descartar = QPushButton("Descartar")
        self.btn_descartar.clicked.connect(self.descartar_foto)
        self.btn_descartar.hide()

        self.btn_ver_foto = QPushButton("Mostrar imagem selecionada")
        self.btn_ver_foto.clicked.connect(self.mostrar_foto_selecionada)

        self.btn_voltar = QPushButton("Ligar webcam")
        self.btn_voltar.clicked.connect(self.retoma_webcam)

        botoes = QHBoxLayout()
        botoes.addWidget(self.btn_capturar)
        botoes.addWidget(self.btn_guardar)
        botoes.addWidget(self.btn_descartar)
        botoes.addWidget(self.btn_ver_foto)
        botoes.addWidget(self.btn_voltar)

        esquerda = QVBoxLayout()
        esquerda.addWidget(self.area_video)
        esquerda.addLayout(botoes)

        # Lista lateral
        self.lista_widget = QListWidget()
        self.lista_widget.setFixedWidth(250)
        self.lista_widget.itemClicked.connect(self.mostrar_foto)

        self.btn_importar = QPushButton("Importar")
        self.btn_importar.clicked.connect(self.importar_foto)
        self.btn_exportar = QPushButton("Exportar")
        self.btn_exportar.clicked.connect(self.exportar_foto)
        self.btn_eliminar = QPushButton("Eliminar")
        self.btn_eliminar.clicked.connect(self.eliminar_foto)

        direita = QVBoxLayout()
        direita.addWidget(QLabel("Imagens"))
        direita.addWidget(self.lista_widget)
        direita.addWidget(self.btn_importar)
        direita.addWidget(self.btn_exportar)
        direita.addWidget(self.btn_eliminar)

        layout.addLayout(esquerda)
        layout.addLayout(direita)
        self.setLayout(layout)

    def atualizar_frame(self):
        if not self.modo_foto:
            ret, frame = self.webcam.read()
            if ret:
                self.display_frame(frame)

    def display_frame(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (500, 350))
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        qimg = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        self.area_video.setPixmap(QPixmap.fromImage(qimg))

    def tirar_foto(self):
        ret, frame = self.webcam.read()
        if ret:
            self.foto_temporaria = frame.copy()
            self.display_frame(frame)
            self.timer.stop()
            self.btn_capturar.setEnabled(False)
            self.btn_guardar.show()
            self.btn_descartar.show()

    def guardar_foto(self):
        if self.foto_temporaria is not None:
            nome_foto = f"foto_{len(self.lista_fotos)}.jpg"
            cv2.imwrite(nome_foto, self.foto_temporaria)
            self.lista_fotos.append(nome_foto)
            self.lista_widget.addItem(nome_foto)
            self.foto_temporaria = None
        self.retoma_webcam()

    def descartar_foto(self):
        self.foto_temporaria = None
        self.retoma_webcam()

    def retoma_webcam(self):
        self.modo_foto = False
        self.btn_guardar.hide()
        self.btn_descartar.hide()
        self.btn_capturar.setEnabled(True)
        self.timer.start(30)

    def importar_foto(self):
        caminho, _ = QFileDialog.getOpenFileName(self, "Importar", "", "Imagens (*.png *.jpg *.jpeg)")
        if caminho:
            self.lista_fotos.append(caminho)
            self.lista_widget.addItem(os.path.basename(caminho))

    def exportar_foto(self):
        item = self.lista_widget.currentItem()
        if item:
            idx = self.lista_widget.row(item)
            origem = self.lista_fotos[idx]
            destino, _ = QFileDialog.getSaveFileName(self, "Exportar", "", "Imagens (*.png *.jpg *.jpeg)")
            if destino:
                try:
                    with open(origem, "rb") as f: dados = f.read()
                    with open(destino, "wb") as f: f.write(dados)
                except Exception as e:
                    QMessageBox.warning(self, "Erro", f"Erro ao exportar: {e}")

    def eliminar_foto(self):
        item = self.lista_widget.currentItem()
        if item:
            idx = self.lista_widget.row(item)
            self.lista_widget.takeItem(idx)
            caminho = self.lista_fotos.pop(idx)
            if os.path.exists(caminho) and caminho.startswith("foto_"):
                os.remove(caminho)

    def mostrar_foto(self, item):
        idx = self.lista_widget.row(item)
        caminho = self.lista_fotos[idx]
        pixmap = QPixmap(caminho).scaled(500, 350, Qt.AspectRatioMode.KeepAspectRatio)
        self.area_video.setPixmap(pixmap)

    def mostrar_foto_selecionada(self):
        self.mostrar_foto(self.lista_widget.currentItem())
        self.modo_foto = True
        self.timer.stop()


class AbaProcessamento(QWidget):
    def __init__(self):
        super().__init__()
        self.img = None
        self.img_display = None
        self.img_original = None
        self.initUI()

    def initUI(self):
        layout = QHBoxLayout()

        # Controles
        self.filtros = {}
        self.sliders = {}
        controles = QVBoxLayout()

        btn_abrir = QPushButton("Abrir Imagem")
        btn_abrir.clicked.connect(self.abrir_imagem)
        controles.addWidget(btn_abrir)

        for nome in ["Preto e branco", "Desfoque", "Brilho", "Contraste", "Nitidez", "Saturação"]:
            chk = QCheckBox(nome)
            self.filtros[nome] = chk
            controles.addWidget(chk)
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setMinimum(1)
            slider.setMaximum(10)
            slider.setValue(1)
            self.sliders[nome] = slider
            controles.addWidget(slider)

        btn_aplicar = QPushButton("Aplicar")
        btn_aplicar.clicked.connect(self.aplicar_filtros)
        controles.addWidget(btn_aplicar)

        btn_reverter = QPushButton("Reverter para original")
        btn_reverter.clicked.connect(self.reverter_original)
        controles.addWidget(btn_reverter)

        layout.addLayout(controles)

        # Imagens lado a lado
        self.label_antes = QLabel("Antes")
        self.label_depois = QLabel("Depois")
        layout.addWidget(self.label_antes)
        layout.addWidget(self.label_depois)

        self.setLayout(layout)

    def abrir_imagem(self):
        path, _ = QFileDialog.getOpenFileName(self, "Abrir Imagem", "", "Imagens (*.png *.jpg *.jpeg)")
        if path:
            self.img = cv2.imread(path)
            self.img_display = self.img.copy()
            self.img_original = self.img.copy()
            self.exibir_imagem(self.label_antes, self.img)

    def aplicar_filtros(self):
        if self.img is None: return
        imagem = self.img.copy()
        for nome, chk in self.filtros.items():
            if chk.isChecked():
                valor = self.sliders[nome].value()
                imagem = self.aplicar_filtro(imagem, nome, valor)
        self.img_display = imagem
        self.exibir_imagem(self.label_depois, imagem)

    def reverter_original(self):
        if self.img_original is not None:
            self.exibir_imagem(self.label_antes, self.img_original)
            self.label_depois.clear()

    def exibir_imagem(self, label, imagem):
        imagem_rgb = cv2.cvtColor(imagem, cv2.COLOR_BGR2RGB)
        h, w, ch = imagem_rgb.shape
        bytes_por_linha = ch * w
        qimg = QImage(imagem_rgb.data, w, h, bytes_por_linha, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg).scaled(400, 400, Qt.AspectRatioMode.KeepAspectRatio)
        label.setPixmap(pixmap)

    def aplicar_filtro(self, imagem, tipo, valor):
        if tipo == "Preto e branco":
            return cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
        elif tipo == "Desfoque":
            valor = max(1, valor // 2 * 2 + 1)
            return cv2.GaussianBlur(imagem, (valor, valor), 0)
        elif tipo == "Brilho":
            return cv2.convertScaleAbs(imagem, alpha=1, beta=valor*10)
        elif tipo == "Contraste":
            return cv2.convertScaleAbs(imagem, alpha=1 + valor/10, beta=0)
        elif tipo == "Nitidez":
            kernel = np.array([[0, -1, 0], [-1, valor, -1], [0, -1, 0]])
            return cv2.filter2D(imagem, -1, kernel)
        elif tipo == "Saturação":
            hsv = cv2.cvtColor(imagem, cv2.COLOR_BGR2HSV)
            hsv[..., 1] = np.clip(hsv[..., 1] + valor*10, 0, 255)
            return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        return imagem


class ProgramaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Projeto de Engenharia e Automação Industrial")
        self.setFixedSize(1000, 600)

        tabs = QTabWidget()
        tabs.addTab(AbaGerir(), "Gerir")
        tabs.addTab(AbaProcessamento(), "Processamento")
        # Aqui puedes agregar outra aba de classificação no futuro

        self.setCentralWidget(tabs)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = ProgramaPrincipal()
    janela.show()
    sys.exit(app.exec())
