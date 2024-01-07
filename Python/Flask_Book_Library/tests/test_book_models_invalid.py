import pytest
from random import randint, choice, randrange
from string import ascii_letters
from datetime import date

from project.books.models import Book

# constants
MAX_NAME_LENGTH = 64
MAX_AUTHOR_LENGTH = 64
MAX_BOOK_TYPE_LENGTH = 20
MAX_STATUS_LENGTH = 20
MAX_YEAR_PUBLISHED = date.today().year
ITERATIONS_PER_TEST = 10

random_valid_string_length = randint(1, 20)
random_valid_year_published = randint(1439, MAX_YEAR_PUBLISHED) # Since Gutenberg invention

class Test_Book_Models_Invalid:
    @pytest.fixture
    def example_valid_data(self):
        return {
            "name": "The Great Book",
            "author": "John Doe",
            "year_published": 1998,
            "book_type": "poem",
            "status": "not available"
        }

    @pytest.fixture
    def example_invalid_type_data(self):
        return {
            "name": 2,
            "author": 3,
            "year_published": "xow",
            "book_type": 4,
            "status": 5
        }
    
    @pytest.fixture
    def naughty_strings(self):
        return [
            None,
            "None",
            "null",
            "0",
            "",
            " ",
            "   ",
            "\t",
            "\n",
            "john.doe\n@hospital.com",
            "田中さんにあげて下さい",
            "ßÎËYä~½ÌÞ#ù/ã#K_¯V:_~½ÞøDy¬EÚnF÷í$",
            "Ó|åTf½zDðNÓo´ýAwRïÓ@ÿLFãÈ5ò¹Èþ\\()¢0ÂÛ",
            "사회과학원 어학연구소",
            '<foo val=“bar” />',
            """
            "'"'"''''"
            """,
            "Ⱥ Ⱦ",
            ",。・:*:・゜’( ☻ ω ☻ )。・:*:・゜’",
            "( ͡° ͜ʖ ͡°)",
            "🆗 ",
            "בָּרָא אֱלֹהִים, אֵת הַשָּׁמַיִם, וְאֵת הָאָרֶץ",
            "الْقَائِمَةِ وَفِيم يَخُصَّ التَّطْبِيقَا",
            "‪‪test‪",
            "͎ ̢̼̻̱̘h͚͎͙̜̣̲ͅi̦̲̣̰̤v̻͍e̺̭̳̪̰-m̢iͅn̖̺̞̲̯̰d̵̼̟͙̩̼̘̳ ̞̥̱̳̭r̛̗̘e͙p͠r̼̞̻̭̗e̺̠̣͟s̘͇̳͍̝͉e͉̥̯̞̲͚̬͜ǹ̬͎͎̟̖͇̤t͍̬̤͓̼̭͘ͅi̪̱n͠g̴͉ ͏͉ͅc̬̟h͡a̫̻̯͘o̫̟̖͍̙̝͉s̗̦̲.̨", 
            """
            %25f6
            %25f7
            %25f8
            %25f9
            %25fa
            %25fb
            %25fc
            %25fd
            """,
            str(bytes(randrange(0,255) for _ in range(128))) # random bytes
        ]


    @pytest.fixture(params=[random_valid_string_length])
    def get_random_string(self, request):
        random_string = lambda length: ''.join(choice(ascii_letters) for i in range(length))
        yield random_string(request.param)

    def test_name_incorrect_type(self, example_valid_data, example_invalid_type_data):
        _, author, year_published, book_type, status = example_valid_data.values()
        invalid_name, _, _, _, _ = example_invalid_type_data.values()
        with pytest.raises(TypeError):
            book = Book(
                name=invalid_name,
                author=author,
                year_published=year_published,
                book_type=book_type,
                status=status
            )
        assert isinstance(book.name, str)
        

    def test_name_out_of_bounds_value(self, example_valid_data):
        _, author, year_published, book_type, status = example_valid_data.values()
        invalid_name = "x" * (MAX_NAME_LENGTH + 1)
        with pytest.raises(ValueError):
            book = Book(
                name=invalid_name,
                author=author,
                year_published=year_published,
                book_type=book_type,
                status=status
            )
        if book.name:
            assert len(book.name) <= MAX_NAME_LENGTH

    def test_author_incorrect_type(self, example_valid_data, example_invalid_type_data):
        name, _, year_published, book_type, status = example_valid_data.values()
        _, invalid_author, _, _, _ = example_invalid_type_data.values()
        with pytest.raises(TypeError):
            book = Book(
                name=name,
                author=invalid_author,
                year_published=year_published,
                book_type=book_type,
                status=status
            )
        assert isinstance(book.author, str)

    def test_author_out_of_bounds_value(self, example_valid_data):
        name, _, year_published, book_type, status = example_valid_data.values()
        invalid_author = "x" * (MAX_AUTHOR_LENGTH + 1)
        with pytest.raises(ValueError):
            book = Book(
                name=name,
                author=invalid_author,
                year_published=year_published,
                book_type=book_type,
                status=status
            )
        if book.author:
            assert len(book.author) <= MAX_AUTHOR_LENGTH

    def test_year_published_incorrect_type(self, example_valid_data, example_invalid_type_data):
        name, author, _, book_type, status = example_valid_data.values()
        _, _, invalid_year_published, _, _ = example_invalid_type_data.values()
        with pytest.raises(TypeError):
            book = Book(
                name=name,
                author=author,
                year_published=invalid_year_published,
                book_type=book_type,
                status=status
            )
        if book.year_published:
            assert isinstance(book.year_published, int)

    def test_year_published_out_of_bounds_value(self, example_valid_data):
        name, author, _, book_type, status = example_valid_data.values()
        invalid_year_published = MAX_YEAR_PUBLISHED + 1
        with pytest.raises(ValueError):
            book = Book(
                name=name,
                author=author,
                year_published=invalid_year_published,
                book_type=book_type,
                status=status
            )
        if book.year_published:
            assert len(book.year_published) <= MAX_YEAR_PUBLISHED

    def test_book_type_incorrect_type(self, example_valid_data, example_invalid_type_data):
        name, author, year_published, _, status = example_valid_data.values()
        _, _, _, invalid_book_type, _ = example_invalid_type_data.values()
        with pytest.raises(TypeError):
            book = Book(
                name=name,
                author=author,
                year_published=year_published,
                book_type=invalid_book_type,
                status=status
            )
        if book.book_type:
            assert isinstance(book.book_type, str)

    def test_book_type_out_of_bounds_value(self, example_valid_data):
        name, author, year_published, _, status = example_valid_data.values()
        invalid_book_type = "x" * (MAX_BOOK_TYPE_LENGTH + 1)
        with pytest.raises(ValueError):
            book = Book(
                name=name,
                author=author,
                year_published=year_published,
                book_type=invalid_book_type,
                status=status
            )
        if book.book_type:
            assert len(book.book_type) <= MAX_BOOK_TYPE_LENGTH

    def test_status_incorrect_type(self, example_valid_data, example_invalid_type_data):
        name, author, year_published, book_type, _ = example_valid_data.values()
        _, _, _, _, invalid_status = example_invalid_type_data.values()
        with pytest.raises(TypeError):
            book = Book(
                name=name,
                author=author,
                year_published=year_published,
                book_type=book_type,
                status=invalid_status
            )
        if book.status:
            assert isinstance(book.status, str)

    def test_status_out_of_bounds_value(self, example_valid_data):
        name, author, year_published, _, status = example_valid_data.values()
        invalid_book_type = "x" * (MAX_BOOK_TYPE_LENGTH + 1)
        with pytest.raises(ValueError):
            book = Book(
                name=name,
                author=author,
                year_published=year_published,
                book_type=invalid_book_type,
                status=status
            )
        if book.status:
            assert len(book.status) <= MAX_STATUS_LENGTH

    def test_status_against_odd_strings(self, naughty_strings):
        for string in naughty_strings:
            book = Book(
                name=string,
                author=string,
                year_published=2022,
                book_type=string,
                status=string
            )
        assert isinstance(book.__repr__(), str)
        


if __name__ == "__main__":
    raise NotImplementedError("Use run_tests.bash")