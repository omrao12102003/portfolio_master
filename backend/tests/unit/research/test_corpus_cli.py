from app.research import corpus_cli


def test_corpus_cli_module_exposes_main():
    assert callable(corpus_cli.main)
