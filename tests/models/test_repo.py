import pytest

from docbuild.models.repo import Repo


@pytest.fixture
def repo_url() -> str:
    return 'https://github.com/org/repo.git'


@pytest.mark.parametrize(
    'input_value, name, url',
    [
        # 1
        (
            'https://github.com/org/repo.git',
            'org/repo',
            'https://github.com/org/repo.git',
        ),
        # 2
        ('https://github.com/ORG/repo', 'org/repo', 'https://github.com/org/repo.git'),
        # 3
        ('https://github.com/org/repo', 'org/repo', 'https://github.com/org/repo.git'),
        # 4
        ('https://github.com/org/repo/', 'org/repo', 'https://github.com/org/repo.git'),
    ],
)
def test_repo_https(input_value, name, url):
    repo = Repo(input_value)
    assert repo.name == name
    assert repo.url == url


@pytest.mark.parametrize(
    'input_value, name, url',
    [
        # 1
        ('git@github.com:org/repo.git', 'org/repo', 'https://github.com/org/repo.git'),
        # 2
        ('git@github.com:ORG/repo.git', 'org/repo', 'https://github.com/org/repo.git'),
        # 3
        ('git@github.com:org/repo', 'org/repo', 'https://github.com/org/repo.git'),
        # 4
        ('git@github.com:org/repo/', 'org/repo', 'https://github.com/org/repo.git'),
    ],
)
def test_repo_ssh(input_value, name, url):
    repo = Repo(input_value)
    assert repo.name == name
    assert repo.url == url


@pytest.mark.parametrize(
    'input_value, name, url',
    [
        # 1
        ('gh://org/repo', 'org/repo', 'https://github.com/org/repo.git'),
        # 2
        ('gh://ORG/repo', 'org/repo', 'https://github.com/org/repo.git'),
        # 3
        ('gh://org/repo/', 'org/repo', 'https://github.com/org/repo.git'),
        # 4
        ('gh://org/repo.git', 'org/repo', 'https://github.com/org/repo.git'),
    ],
)
def test_repo_abbreviation(input_value, name, url):
    repo = Repo(input_value)
    assert repo.name == name
    assert repo.url == url


@pytest.mark.parametrize(
    'input_value, surl',
    [
        # 1
        ('https://github.com/org/repo.git', 'gh://org/repo'),
        # 2
        ('https://gitlab.com/ORG/repo.git', 'gl://org/repo'),
        # 3
        ('git@github.com:org/repo.git', 'gh://org/repo'),
        # 4
        ('gh://org/repo', 'gh://org/repo'),
        # 5
        ('gh://ORG/repo', 'gh://org/repo'),
        # 6
        ('gh://org/repo/', 'gh://org/repo'),
        # 7
        ('gh://org/repo.git', 'gh://org/repo'),
    ],
)
def test_repo_with_surl(input_value, surl):
    repo = Repo(input_value)
    assert repo.surl == surl


def test_repo_with_unknown_abbreviation():
    with pytest.raises(ValueError):
        Repo('fake://org/repo')


@pytest.mark.parametrize(
    'input_value, name, url',
    [
        # 1
        ('org/repo', 'org/repo', 'https://github.com/org/repo.git'),
        # 2
        ('ORG/repo', 'org/repo', 'https://github.com/org/repo.git'),
    ],
)
def test_repo_abbreviated(input_value, name, url):
    repo = Repo(input_value)
    assert repo.name == name
    assert repo.url == url


def test_repo_with_empty_value():
    with pytest.raises(ValueError):
        Repo('')


def test_repo_with_invalid_value():
    with pytest.raises(ValueError):
        Repo('invalid-repo-value')


def test_repo_compare_with_eq(repo_url):
    repo1 = Repo(repo_url)
    repo2 = Repo('https://github.com/ORG/repo.git')
    assert repo1 == repo2
    assert 'org/repo' == repo1
    assert object() != repo1


def test_repo_compare_with_in(repo_url):
    repo = Repo(repo_url)
    assert 'org/repo' in repo
    assert object() not in repo  # type: ignore


def test_repo_hash(repo_url):
    repo = Repo(repo_url)
    assert hash(repo) == hash(repo.name)


def test_repo_slug(repo_url):
    repo = Repo(repo_url)
    assert repo.slug == 'https___github_com_org_repo_git'


def test_repo_surl(repo_url):
    repo = Repo(repo_url)
    assert repo.surl == 'gh://org/repo'


def test_repo_str(repo_url):
    repo = Repo(repo_url)
    assert str(repo) == repo_url
