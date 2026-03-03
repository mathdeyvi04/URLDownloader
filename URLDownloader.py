import yt_dlp
from pprint import pprint

class URLDownloader:
    """
    @brief Responsável prover a representar a aplicação como um todo e separar responsabilidades.
    """

    def __init__(self) -> None:
        """
        @brief Iniciará a aplicação com seus atributos mínimos.
        """
        pass

    def _init_download(self, link: str, only_audio: bool = False) -> bool:
        """

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

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])

    def mainloop(self) -> None:
        """

        """
        self._init_download("https://www.youtube.com/watch?v=YxFFfQpdUME")

        pass


if __name__ == "__main__":
    URLDownloader().mainloop()
