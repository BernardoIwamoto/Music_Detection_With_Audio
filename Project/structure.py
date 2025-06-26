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
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
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
        print("Verificando cache de vetores...")

        cache_dir = "projeto/cache"
        os.makedirs(cache_dir, exist_ok=True)
        cache_dados = os.path.join(cache_dir, "vetores.npy")
        cache_arquivos = os.path.join(cache_dir, "nomes.npy")
        cache_estilos = os.path.join(cache_dir, "estilos.npy")

        if os.path.exists(cache_dados) and os.path.exists(cache_arquivos) and os.path.exists(cache_estilos):
            print("Cache encontrado. Carregando dados...")
            self.todos_dados = np.load(cache_dados, allow_pickle=True)
            self.arquivos = np.load(cache_arquivos, allow_pickle=True)
            self.estilos = np.load(cache_estilos, allow_pickle=True)
            return

        print("Cache não encontrado. Lendo músicas da pasta...")
        self.todos_dados = []
        self.arquivos = []
        self.estilos = []

        for raiz, _, arquivos in os.walk(self.pasta):
            for nome in arquivos:
                if nome.lower().endswith((".wav", ".mp3")):
                    caminho = os.path.join(raiz, nome)
                    try:
                        vetor = self._extrair_caracteristicas(caminho)
                        estilo = os.path.basename(os.path.normpath(os.path.dirname(caminho)))
                        self.todos_dados.append(vetor)
                        self.arquivos.append(caminho)
                        self.estilos.append(estilo)
                    except Exception as e:
                        print(f"Erro com {os.path.basename(caminho)}: {e}")

        self.todos_dados = np.array(self.todos_dados)
        print(f"{len(self.arquivos)} arquivos processados com sucesso.")

        np.save(cache_dados, self.todos_dados)
        np.save(cache_arquivos, self.arquivos)
        np.save(cache_estilos, self.estilos)
        print("Cache salvo com sucesso.")

    def _resumir_informacoes(self):
        print("Organizando as informações principais das músicas...")
        self.reducao = PCA(n_components=2)
        self.musicas_em_2d = self.reducao.fit_transform(self.todos_dados)

    def _agrupar_musicas(self):
        print("Agrupando músicas com som parecido...")
        agrupador = KMeans(n_clusters=self.total_grupos, random_state=42)
        self.grupos = agrupador.fit_predict(self.musicas_em_2d)

    def mostrar_mapa(self):
        plt.figure(figsize=(12, 7))
        cores = plt.cm.tab10(np.linspace(0, 1, self.total_grupos))

        for i in range(self.total_grupos):
            indices = np.where(self.grupos == i)
            plt.scatter(
                self.musicas_em_2d[indices, 0],
                self.musicas_em_2d[indices, 1],
                color=cores[i],
                label=f"Grupo {i} ({len(indices[0])} músicas)",
                s=40
            )

        plt.title("Análise de Clusters de Músicas por Similaridade Sonora", fontsize=14)
        plt.xlabel("Eixo 1 (PCA)", fontsize=12)
        plt.ylabel("Eixo 2 (PCA)", fontsize=12)
        plt.legend(loc='best', fontsize=10)
        plt.grid(True, linestyle="--", alpha=0.3)
        plt.tight_layout()
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

    def limpar_cache(self):
        cache_dir = "projeto/cache"
        arquivos = ["vetores.npy", "nomes.npy", "estilos.npy"]

        removidos = 0
        for nome in arquivos:
            caminho = os.path.join(cache_dir, nome)
            if os.path.exists(caminho):
                os.remove(caminho)
                removidos += 1

        print(f"{removidos} arquivos de cache removidos.")
