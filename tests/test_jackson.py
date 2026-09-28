import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from agentra import jackson


class FakeModel:
    def __init__(self):
        self.calls = []

    def ask(self, instruction, payload):
        self.calls.append((instruction, payload))
        if "manager of AGENTRA" in instruction:
            return {"agents": [{"role": "Python specialist", "task": "Implement feature"}]}
        if "independent QA reviewer" in instruction:
            return {"approved": len(self.calls) >= 5, "issues": ["Fix the output"], "summary": "Verified"}
        if "responsible specialist" in instruction:
            return {"changes": [{"path": "feature.py", "content": "print('fixed')\n"}], "summary": "Fixed"}
        return {"changes": [{"path": "feature.py", "content": "print('initial')\n"}], "summary": "Done"}


class JacksonTests(unittest.TestCase):
    def test_rejects_sensitive_paths_and_symlink_escape(self):
        with tempfile.TemporaryDirectory() as temp:
            with patch.object(jackson, "ROOT", Path(temp).resolve()):
                for name in ("../escape.py", ".github/workflows/job.yml", ".env", "/tmp/file.py", "secret.key"):
                    with self.subTest(name=name), self.assertRaises(ValueError):
                        jackson.safe_path(name)
                (Path(temp) / "out").symlink_to("/tmp", target_is_directory=True)
                with self.assertRaises(ValueError):
                    jackson.safe_path("out/file.py")

    def test_dynamic_team_and_correction_loop(self):
        with tempfile.TemporaryDirectory() as temp:
            import subprocess
            subprocess.run(["git", "init", "-q", temp], check=True)
            root = Path(temp).resolve()
            with patch.object(jackson, "ROOT", root):
                model = FakeModel()
                result = jackson.run(model, "Build feature")
                self.assertEqual(result["rounds"], 2)
                self.assertEqual(result["agents"][0]["role"], "Python specialist")
                self.assertEqual((root / "feature.py").read_text(), "print('fixed')\n")
                review_payload = next(payload for instruction, payload in model.calls if "independent QA reviewer" in instruction)
                self.assertIn("print('initial')", review_payload)


if __name__ == "__main__":
    unittest.main()
