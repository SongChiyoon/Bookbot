class books(object):
    def __init__(self):
        self._title = None
        self._imageURL = None
        self._total = None
        self._author = None
        self._description = None
        self._price = None
        self._publisher = None
        self._link = None

    def setTitle(self, title):
        self._title = title

    def setTotal(self, total):
        self._total = total

    def setImageURL(self, image):
        self._imageURL = image

    def setAuthoor(self, author):
        self._author = author
    def setPrice(self, price):
        self._price = price

    def setPublisher(self, publisher):
        self._publisher = publisher

    def setDescription(self, description):
        self._description = description

    def setLink(self, link):
        self._link = link

    def Title(self):
        return self._title
    def Total(self):
        return self._total
    def ImageURL(self):
        return self._imageURL
    def Author(self):
        return self._author
    def Price(self):
        return self._price
    def Publisher(self):
        return self._publisher
    def Description(self):
        return self._description
    def Link(self):
        return self._link