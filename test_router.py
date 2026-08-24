from service.classification.router import classify_path


def test_classify_path_marks_executables_for_hold():
    tier = classify_path("C:/Users/test/Downloads/setup.exe")
    assert tier == "executable"


def test_classify_path_marks_text_files_as_fast_tier():
    tier = classify_path("C:/Users/test/Downloads/readme.txt")
    assert tier == "fast"
