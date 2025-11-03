def gif_url(name):
    return f"/static/gifs/{name}.gif"

def letters_urls(text):
    return [f"/static/letters/{c}.jpg" for c in text if c.isalpha()]
