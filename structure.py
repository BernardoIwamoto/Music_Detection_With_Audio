import os
import numpy as np
import librosa
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

class OrganizadorMusical:
    def __init__(self, pasta_de_musicas, grupos=8):
        self.pasta = pasta_de_musicas
        self.total_grupos = grupos
        self.arquivos = []
        self.estilos = []
        self._carregar_musicas()
        self._resumir_informacoes()
        self._agrupar_musicas()

    def _extrair_caracteristicas(self, caminho_audio):
        y, sr = librosa.load(caminho_audio, sr=None)
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20)
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        contraste = librosa.feature.spectral_contrast(y=y, sr=sr)

        return np.concatenate([
            np.mean(mfcc, axis=1),
            np.std(mfcc, axis=1),
            np.mean(chroma, axis=1),
            np.std(chroma, axis=1),
            np.mean(contraste, axis=1),
            np.std(contraste, axis=1),
        ])

    def _carregar_musicas(self):
        print("Lendo músicas da pasta...")
        self.todos_dados = []

        for raiz, _, arquivos in os.walk(self.pasta):
            for nome in arquivos:
                if nome.lower().endswith(".wav"):
                    caminho = os.path.join(raiz, nome)
                    try:
                        vetor = self._extrair_caracteristicas(caminho)
                        self.todos_dados.append(vetor)
                        self.arquivos.append(caminho)
                        self.estilos.append(os.path.basename(raiz))
                    except Exception as e:
                        print(f"Erro com {nome}: {e}")

        self.todos_dados = np.array(self.todos_dados)

    def _resumir_informacoes(self):
        print("Organizando as informações principais das músicas...")
        self.reducao = PCA(n_components=2)
        self.musicas_em_2d = self.reducao.fit_transform(self.todos_dados)

    def _agrupar_musicas(self):
        print("Agrupando músicas com som parecido...")
        agrupador = KMeans(n_clusters=self.total_grupos, random_state=42)
        self.grupos = agrupador.fit_predict(self.musicas_em_2d)

    def mostrar_mapa(self):
        print("Gerando mapa musical...")
        plt.figure(figsize=(10, 6))
        for g in range(self.total_grupos):
            pontos = np.where(self.grupos == g)
            plt.scatter(self.musicas_em_2d[pontos, 0], self.musicas_em_2d[pontos, 1], label=f'Grupo {g}')
        plt.title("Mapa de Músicas por Estilo Sonoro")
        plt.xlabel("Eixo 1")
        plt.ylabel("Eixo 2")
        plt.legend()
        plt.show()

    def sugerir_musicas_parecidas(self, caminho_novo):
        print(f"Analisando: {os.path.basename(caminho_novo)}")
        vetor = self._extrair_caracteristicas(caminho_novo).reshape(1, -1)
        vetor_2d = self.reducao.transform(vetor)
        
        distancias = np.linalg.norm(self.musicas_em_2d - vetor_2d, axis=1)
        mais_parecidos = distancias.argsort()[:5]

        print("Músicas mais parecidas encontradas:")
        for i in mais_parecidos:
            print(f" - {os.path.basename(self.arquivos[i])}")
