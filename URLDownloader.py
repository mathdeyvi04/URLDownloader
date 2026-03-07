import yt_dlp
from os.path import basename
from prompt_toolkit import PromptSession
from concurrent.futures import ThreadPoolExecutor
from time import sleep

class URLDownloader:
    """
    @class URLDownloader
    @brief Responsável por gerenciar downloads de URLs utilizando um pool de threads.

    @details
    Esta classe encapsula a lógica de download utilizando a biblioteca yt_dlp e
    o ThreadPoolExecutor para permitir downloads simultâneos. Também mantém
    controle interno do progresso de cada download iniciado.
    """

    def __init__(self, max_workers: int = 4) -> None:
        """
        @brief Construtor da classe URLDownloader.

        @details
        Inicializa o executor responsável por gerenciar as threads de download
        e prepara as estruturas internas para controle do progresso das tarefas.

        @param max_workers Número máximo de downloads simultâneos permitidos.
        """

        self._max_workers = max_workers
        self._current_downloads = []
        self._next_id = 0
        self.show_downloads = True
        self._executor = ThreadPoolExecutor(max_workers=self._max_workers)

    def _hook_for_the_progress(self, object_in_download: dict, download_id: int) -> None:
        """
        @brief Callback responsável por atualizar o progresso de um download.

        @details
        Este método é registrado como um progress_hook do yt_dlp. Ele recebe
        informações periódicas sobre o estado do download e atualiza os dados
        armazenados internamente na estrutura _current_downloads.

        @param object_in_download Dicionário contendo informações do progresso
        fornecidas pelo yt_dlp.
        @param download_id Identificador interno do download sendo monitorado.
        """

        item = self._current_downloads[download_id]

        if object_in_download["status"].startswith('d'):
            total = (
                object_in_download.get("total_bytes")
                or object_in_download.get("total_bytes_estimate")
                or 0
            )

            downloaded = object_in_download.get("downloaded_bytes", 0)

            item["percent"] = int((downloaded / total) * 100) if total else 0

            if not item["name"]:
                item["name"] = basename(
                    object_in_download.get("filename", "")
                )

        elif object_in_download["status"].startswith('f'):
            item["percent"] = 100

    def _init_download(self, download_id: int, link: str, only_audio: bool = False) -> bool:
        """
        @brief Executa o processo de download de uma URL específica.

        @details
        Este método atua como worker do ThreadPoolExecutor. Ele configura
        as opções do yt_dlp e inicia o download do recurso indicado. O
        progresso do download é monitorado por meio de callbacks.

        @param download_id Identificador interno do download.
        @param link URL do conteúdo que será baixado.
        @param only_audio Indica se apenas o áudio deve ser extraído.

        @return bool
        @retval True Download finalizado com sucesso.
        @retval False Ocorreu algum erro durante o processo.
        """

        ydl_opts = {
            "outtmpl": "./%(title)s.%(ext)s",
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
            "merge_output_format": "mp4",
        } if not only_audio else {
            "outtmpl": "./%(title)s.%(ext)s",
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "0",
            }],
        }

        ydl_opts.update(
            {
                "quiet": True,
                "noprogress": True,
                "no_warnings": True,
                "progress_hooks": [
                    lambda object_in_download, i=download_id:
                    self._hook_for_the_progress(object_in_download, i)
                ],
            }
        )

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([link])

            print("-- Download Bem Sucedido")
            return True

        except Exception as error:
            print(f"Houve um erro no download: {error}")
            # Então podemos eliminar o download
            self._current_downloads.pop(download_id - 1)
            return False

    def _clear_historic_downloads(self) -> None:
        """
        @brief Limpa o histórico de downloads finalizados.

        @details
        Este método verifica se todos os downloads registrados já foram
        concluídos. Caso nenhum esteja em andamento, a lista de downloads
        atuais é esvaziada para evitar crescimento desnecessário da estrutura.
        """

        if not any(
            filter(
                lambda item: item["percent"] != 100,
                self._current_downloads,
            )
        ) and self._current_downloads:
            self._next_id = 0
            self._current_downloads.clear()

    def commit_download(self, url: str, only_audio: bool = False) -> int:
        """
        @brief Registra e inicia um novo download.

        @details
        Adiciona um novo download ao sistema e o agenda para execução
        no ThreadPoolExecutor. Cada download recebe um identificador único.

        A estratégia adotada não reutiliza IDs anteriores, evitando possíveis
        problemas de sincronização ou colisão de referências.

        @param url URL do conteúdo que será baixado.
        @param only_audio Indica se apenas o áudio deve ser baixado.

        @return int
        Identificador único associado ao download iniciado.
        """

        self._clear_historic_downloads()

        download_id = self._next_id
        self._next_id += 1

        self._current_downloads.append(
            {
                "name": "",
                "percent": 0,
            }
        )

        self._executor.submit(
            self._init_download,
            download_id,
            url,
            only_audio,
        )

        return download_id

    def show_historic_downloads(self, bar_size: int = 10) -> str:
        """
        @brief Constrói linhas de progresso ASCII para cada download.

        @details
        Percorre a lista interna de downloads e gera uma representação textual
        do progresso utilizando barras ASCII. Cada linha contém o nome do arquivo,
        a barra de progresso e a porcentagem atual.

        @param bar_size Tamanho da barra de progresso em caracteres.
        """

        lines = []
        for item in self._current_downloads:
            percent = item.get("percent", 0)
            name = item.get("name") or "Obtendo nome..."

            filled = int((percent / 100) * bar_size)
            empty = bar_size - filled

            bar = "[" + "#" * filled + "-" * empty + "]"

            lines.append(f"{bar} {percent:3d}% | {name}")

        return "\n".join(lines)

    def mainloop(self) -> None:
        """
        @brief Loop principal de monitoramento da aplicação.

        @details
        Mantém a execução contínua da aplicação exibindo o estado atual
        dos downloads em andamento. O loop pode ser interrompido através
        de um KeyboardInterrupt (Ctrl+C), momento em que o executor
        é encerrado de forma segura.
        """

        def refresh():
            while self.show_downloads:
                sleep(1)
                self._clear_historic_downloads()
                session.app.invalidate()

        session = PromptSession(bottom_toolbar=self.show_historic_downloads)

        self._executor.submit(refresh)

        try:
            while True:
                input_link = str(session.prompt("(Enter The Link) > "))
                if input_link.lower() == 'q':
                    raise KeyboardInterrupt
                elif not input_link.startswith("https://www.youtube.com/"):
                    print("---> Erro, link não válido.")
                    continue

                input_audio = bool(session.prompt("(Enter The only_audio Option) > "))
                self.commit_download(input_link, input_audio)

        except KeyboardInterrupt:
            self.show_downloads = False
            self._executor.shutdown(wait=False)
            exit()

if __name__ == "__main__":
    URLDownloader().mainloop()
    # https://www.youtube.com/watch?v=zBjJUV-lzHo&pp=ygUOdmlkb2UgZGUgMSBtaW4%3D # Vídeo de 1 min para testes