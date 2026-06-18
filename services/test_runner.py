import subprocess
import tempfile
import os
from pathlib import Path

class JavaTestRunner:
    """
    Exécute des tests unitaires sur le code utilisateur.
    Compare la sortie stdout avec les outputs attendus.
    """
    
    def __init__(self, jdk_path: str = "javac"):
        self.jdk_path = jdk_path
        self.java_path = jdk_path.replace("javac", "java")
    
    def run_test(self, user_code: str, test_cases: list) -> dict:
        """
        test_cases = [
            {"input": "5\n3\n", "expected_output": "8", "description": "Addition simple"},
            {"input": "10\n20\n", "expected_output": "30", "description": "Grands nombres"}
        ]
        """
        results = {
            "passed": 0,
            "failed": 0,
            "tests": [],
            "all_passed": False
        }
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Écrire le code utilisateur
            java_file = Path(tmpdir) / "Main.java"
            java_file.write_text(user_code, encoding='utf-8')
            
            # Compiler
            compile_result = subprocess.run(
                [self.jdk_path, str(java_file)],
                capture_output=True,
                text=True,
                cwd=tmpdir
            )
            
            if compile_result.returncode != 0:
                return {
                    "error": "Compilation failed",
                    "compiler_output": compile_result.stderr,
                    "all_passed": False
                }
            
            # Exécuter chaque test
            for test in test_cases:
                try:
                    run_result = subprocess.run(
                        [self.java_path, "Main"],
                        input=test["input"],
                        capture_output=True,
                        text=True,
                        timeout=5,
                        cwd=tmpdir
                    )
                    
                    actual_output = run_result.stdout.strip()
                    expected = test["expected_output"].strip()
                    passed = actual_output == expected
                    
                    results["tests"].append({
                        "description": test["description"],
                        "input": test["input"],
                        "expected": expected,
                        "actual": actual_output,
                        "passed": passed
                    })
                    
                    if passed:
                        results["passed"] += 1
                    else:
                        results["failed"] += 1
                        
                except subprocess.TimeoutExpired:
                    results["tests"].append({
                        "description": test["description"],
                        "error": "Timeout - boucle infinie ?",
                        "passed": False
                    })
                    results["failed"] += 1
            
            results["all_passed"] = results["failed"] == 0
        
        return results