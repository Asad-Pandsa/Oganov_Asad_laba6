from html.parser import HTMLParser
from pathlib import Path

import pytest


SITE_DIR = Path(__file__).parent / "site"
PHOTO_DIR = Path(__file__).parent / "photo"
ARTISTS = [
    ("van-gogh.html", "Винсент Ван Гог", "van-gogh", "Ван Гог.jpg"),
    ("leonardo.html", "Леонардо да Винчи", "leonardo", "Леонардо да Винчи.jpg"),
    (
        "michelangelo.html",
        "Микеланджело Буонарроти",
        "michelangelo",
        "Микеланджело.jpg",
    ),
]


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.images = []
        self.scripts = []
        self.ids = set()
        self.body_attributes = {}
        self.text = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "a":
            self.links.append(attributes.get("href"))
        elif tag == "img":
            self.images.append(attributes)
        elif tag == "script":
            self.scripts.append(attributes)
        elif tag == "body":
            self.body_attributes = attributes
        element_id = attributes.get("id")
        if element_id:
            self.ids.add(element_id)

    def handle_data(self, data):
        self.text.append(data)


def read_page(filename):
    parser = PageParser()
    parser.feed((SITE_DIR / filename).read_text(encoding="utf-8"))
    return parser


def test_gallery_contains_three_artist_links():
    gallery = read_page("index.html")
    assert [link for link in gallery.links if link and link.endswith(".html")] == [
        artist[0] for artist in ARTISTS
    ]


def test_gallery_portraits_exist():
    gallery = read_page("index.html")
    assert len(gallery.images) == len(ARTISTS)
    for image, artist in zip(gallery.images, ARTISTS):
        assert image["src"].startswith("../photo/")
        assert (PHOTO_DIR / artist[3]).is_file()
        assert image["alt"]


@pytest.mark.parametrize(
    ("filename", "artist_name", "artist_id", "photo_name"), ARTISTS
)
def test_detail_page_has_artist_content_and_valid_return_link(
    filename, artist_name, artist_id, photo_name
):
    page = read_page(filename)
    content = " ".join(page.text)
    assert artist_name in content
    assert "← Вернуться к галерее" in content
    assert "index.html" in page.links
    assert page.body_attributes.get("data-artist-id") == artist_id
    assert any(
        image["src"] == f"../photo/{photo_name}" and image.get("alt")
        for image in page.images
    )
    assert (PHOTO_DIR / photo_name).is_file()


@pytest.mark.parametrize("filename", [artist[0] for artist in ARTISTS])
def test_detail_page_has_counter_and_loads_counter_script(filename):
    page = read_page(filename)
    assert "view-count" in page.ids
    assert {"src": "views.js"} in page.scripts
    assert (SITE_DIR / "views.js").is_file()


def test_view_counter_increments_and_persists_per_artist():
    script = (SITE_DIR / "views.js").read_text(encoding="utf-8")
    assert "localStorage.getItem(storageKey)" in script
    assert "localStorage.setItem(storageKey, String(nextCount))" in script
    assert "counter.textContent = String(nextCount)" in script
    assert "artist-views-${artistId}" in script
