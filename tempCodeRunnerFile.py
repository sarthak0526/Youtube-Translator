def validate_youtube(url):
    try:
        yt = YouTube(url)  # Using pytubefix's YouTube class
    except Exception:
        print("Invalid URL")
        return True
    if yt.length > 600:
        print("Your video is larger than 10 minutes")
        return True
    else:
        print("Your video is less than 10 minutes")
        return False
