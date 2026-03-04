import yt_dlp
import os
from concurrent.futures import ThreadPoolExecutor
from pprint import pprint
from time import sleep # Para testes futuros

class URLDownloader:
    """
    @brief Responsável prover a representar a aplicação como um todo e separar responsabilidades.
    """

    def __init__(self, max_workers: int = 4) -> None:
        """
        @brief Construtor da classe.

        @param max_workers Número máximo de downloads simultâneos.
        """
        self._max_workers = max_workers

        self._current_downloads = []
        self._next_id = 0
        self._executor = ThreadPoolExecutor(max_workers = self._max_workers)


    def _hook_for_the_progress(self, object_in_download: dict, download_id: int) -> None:
        item = self._current_downloads[download_id]

        if object_in_download["status"].startswith('d'):
            # Então ainda está em download
            total = object_in_download.get("total_bytes") or object_in_download.get("total_bytes_estimate") or 0
            downloaded = object_in_download.get("downloaded_bytes", 0)

            item["percent"] = int((downloaded / total) * 100) if total else 0

            if not item["name"]:
                item["name"] = os.path.basename(object_in_download.get("filename", ""))


        elif object_in_download["status"].startswith('f'):
            item["percent"] = 100

    def _init_download(self, download_id: int, link: str, only_audio: bool = False) -> bool:
        """
        @brief Worker interno responsável por um download específico.
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
                "preferredquality": "0",  # melhor qualidade
            }],
        }

        ydl_opts.update(
            {
                "quiet": True,
                "noprogress": True,
                "no_warnings": True,
                "progress_hooks": [lambda object_in_download, i=download_id:self._hook_for_the_progress(object_in_download, i)]
            }
        )

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([link])
        except Exception as error:
            print(f"Houve um erro no download: {error}")

    def commit_download(self, url: str, only_audio: bool = False) -> int:
        """
        @brief Adiciona novo download dinamicamente.
        @details
        Não reutilizaremos slots, isso nos permitirá não nos importarmos com 
        problemas de alocação em local de uso.
        @param url URL a ser baixada.
        @return ID do download.
        """

        if any(
            filter(
                lambda x: x["percent"] != 100,
                self._current_downloads
            )
        ):
            self._current_downloads.clear()

        
        download_id = self._next_id
        self._next_id += 1

        self._current_downloads.append(
            {
                "name": "",
                "percent": 0
            }
        )

        self._executor.submit(
            self._init_download,
            download_id,
            url,
            only_audio
        )
        print("Vim")
        return download_id
        
    def mainloop(self) -> None:
        """

        """
        self.commit_download("https://www.youtube.com/watch?v=YxFFfQpdUME")

        while True:
            sleep(1)
            pprint(self._current_downloads)
        
        pass


if __name__ == "__main__":
    URLDownloader().mainloop()
