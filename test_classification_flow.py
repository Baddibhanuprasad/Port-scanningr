from service.classification.router import classify_path
from service.quarantine.vault import QuarantineVault


def test_executable_classification_and_quarantine(tmp_path):
    sample = tmp_path / 'setup.exe'
    sample.write_bytes(b'MZ')

    vault = QuarantineVault(str(tmp_path / 'quarantine'))
    target = vault.store(str(sample), 'initial hold')

    assert classify_path(str(sample)) == 'executable'
    assert target.exists()
    assert target.read_bytes() == b'MZ'
