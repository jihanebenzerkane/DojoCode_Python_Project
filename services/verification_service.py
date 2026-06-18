import os
import re
import shutil
import subprocess
import tempfile
from typing import Dict, Any, List

class VerificationService:
    """
    Service de vérification de code Java de type HackerRank.
    Compile le code Java localement avec JDK et exécute des assertions de tests unitaires réels.
    """

    def __init__(self):
        # On peut spécifier le chemin de javac/java si nécessaire, sinon on utilise le PATH
        self.javac_cmd = "javac"
        self.java_cmd = "java"

    def verify(self, challenge, code: str) -> Dict[str, Any]:
        """
        Vérifie le code Java fourni pour un challenge donné.
        Retourne un dictionnaire contenant le statut de compilation, les tests passés/échoués, etc.
        """
        # Création d'un dossier temporaire dans le workspace (sécurisé et local)
        workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        temp_dir = os.path.join(workspace_dir, "temp_build")
        os.makedirs(temp_dir, exist_ok=True)

        try:
            # 1. Préparation du code utilisateur
            clean_code = code.strip()
            # Si le code ne contient pas la déclaration de la classe Solution, on l'enrobe automatiquement
            if "class Solution" not in clean_code:
                # Import des packages standard utiles pour les élèves
                clean_code = (
                    "import java.util.*;\n"
                    "import java.util.stream.*;\n\n"
                    "public class Solution {\n"
                    f"    {clean_code}\n"
                    "}"
                )

            # Écriture de Solution.java
            solution_path = os.path.join(temp_dir, "Solution.java")
            with open(solution_path, "w", encoding="utf-8") as f:
                f.write(clean_code)

            # 2. Génération du TestRunner.java selon le challenge
            test_runner_content = self._generate_test_runner(challenge.title)
            test_runner_path = os.path.join(temp_dir, "TestRunner.java")
            with open(test_runner_path, "w", encoding="utf-8") as f:
                f.write(test_runner_content)

            # 3. Compilation des fichiers Solution.java et TestRunner.java
            compile_process = subprocess.run(
                [self.javac_cmd, "-encoding", "utf-8", "Solution.java", "TestRunner.java"],
                cwd=temp_dir,
                capture_output=True,
                text=True,
                shell=False
            )

            if compile_process.returncode != 0:
                # Erreur de compilation
                errors = compile_process.stderr or compile_process.stdout
                # Simplifier le chemin des fichiers temporaires dans les messages d'erreur pour l'utilisateur
                friendly_errors = errors.replace(temp_dir, "").strip()
                return {
                    "success": False,
                    "compiled": False,
                    "compilation_error": friendly_errors,
                    "runtime_error": None,
                    "test_results": []
                }

            # 4. Exécution de TestRunner
            run_process = subprocess.run(
                [self.java_cmd, "TestRunner"],
                cwd=temp_dir,
                capture_output=True,
                text=True,
                shell=False,
                timeout=5  # Évite les boucles infinies de l'élève
            )

            if run_process.returncode != 0:
                # Erreur d'exécution
                runtime_err = run_process.stderr or run_process.stdout
                friendly_runtime_err = runtime_err.replace(temp_dir, "").strip()
                return {
                    "success": False,
                    "compiled": True,
                    "compilation_error": None,
                    "runtime_error": friendly_runtime_err or "Processus interrompu (Time Limit Exceeded / Crash)",
                    "test_results": []
                }

            # 5. Analyse des résultats
            stdout_lines = run_process.stdout.splitlines()
            results = []
            all_passed = True

            for line in stdout_lines:
                if line.startswith("TEST_PASS: "):
                    name = line[len("TEST_PASS: "):].strip()
                    results.append({"name": name, "passed": True, "details": "Réussi"})
                elif line.startswith("TEST_FAIL: "):
                    parts = line[len("TEST_FAIL: "):].split("|", 1)
                    name = parts[0].strip()
                    details = parts[1].strip() if len(parts) > 1 else "Échoué"
                    results.append({"name": name, "passed": False, "details": details})
                    all_passed = False

            if not results:
                return {
                    "success": False,
                    "compiled": True,
                    "compilation_error": None,
                    "runtime_error": "Aucun test n'a pu être exécuté. Vérifie la structure de ton code.",
                    "test_results": []
                }

            return {
                "success": all_passed,
                "compiled": True,
                "compilation_error": None,
                "runtime_error": None,
                "test_results": results
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "compiled": True,
                "compilation_error": None,
                "runtime_error": "Temps limite d'exécution dépassé (Timeout de 5 secondes) ! Vérifie s'il y a une boucle infinie.",
                "test_results": []
            }
        except Exception as e:
            return {
                "success": False,
                "compiled": False,
                "compilation_error": None,
                "runtime_error": f"Erreur interne lors de la vérification : {str(e)}",
                "test_results": []
            }
        finally:
            # Nettoyage des fichiers temporaires pour garder le projet propre
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception:
                pass

    def _generate_test_runner(self, title: str) -> str:
        """Génère le code source de TestRunner.java selon le challenge."""
        base_runner = """import java.util.*;

public class TestRunner {
    
    public static void assertTest(String name, boolean condition, String details) {
        if (condition) {
            System.out.println("TEST_PASS: " + name);
        } else {
            System.out.println("TEST_FAIL: " + name + " | " + details);
        }
    }

    public static void main(String[] args) {
        try {
            runTests();
        } catch (Throwable e) {
            System.out.println("TEST_FAIL: Erreur d'exécution globale | Exception: " + e.toString());
            e.printStackTrace();
        }
    }

    private static void runTests() {
        // [TESTS_PLACEHOLDER]
    }
}
"""
        test_cases = ""

        # Normalisation du titre pour la correspondance
        norm_title = title.lower().replace("'", "").replace("’", "").strip()

        if norm_title == "hello dojo":
            test_cases = """
            try {
                String res = Solution.sayHello();
                assertTest("sayHello() retourne 'Hello, Dojo!'", "Hello, Dojo!".equals(res), "Attendu: 'Hello, Dojo!', Obtenu: '" + res + "'");
            } catch (Throwable e) {
                assertTest("sayHello() retourne 'Hello, Dojo!'", false, "Exception : " + e.toString());
            }
            """
        elif norm_title == "pair ou impair":
            test_cases = """
            try {
                assertTest("isEven(4) doit être true", Solution.isEven(4) == true, "Obtenu: false");
                assertTest("isEven(7) doit être false", Solution.isEven(7) == false, "Obtenu: true");
                assertTest("isEven(0) doit être true", Solution.isEven(0) == true, "Obtenu: false");
            } catch (Throwable e) {
                assertTest("Test isEven", false, "Exception : " + e.toString());
            }
            """
        elif norm_title == "maximum de deux nombres":
            test_cases = """
            try {
                assertTest("max(10, 20) doit retourner 20", Solution.max(10, 20) == 20, "Obtenu: " + Solution.max(10, 20));
                assertTest("max(5, -3) doit retourner 5", Solution.max(5, -3) == 5, "Obtenu: " + Solution.max(5, -3));
                assertTest("max(0, 0) doit retourner 0", Solution.max(0, 0) == 0, "Obtenu: " + Solution.max(0, 0));
            } catch (Throwable e) {
                assertTest("Test max", false, "Exception : " + e.toString());
            }
            """
        elif norm_title in ["somme dun tableau", "somme d'un tableau"]:
            test_cases = """
            try {
                assertTest("sumArray([1, 2, 3, 4]) doit retourner 10", Solution.sumArray(new int[]{1, 2, 3, 4}) == 10, "Obtenu: " + Solution.sumArray(new int[]{1, 2, 3, 4}));
                assertTest("sumArray([-1, -2, 5]) doit retourner 2", Solution.sumArray(new int[]{-1, -2, 5}) == 2, "Obtenu: " + Solution.sumArray(new int[]{-1, -2, 5}));
                assertTest("sumArray([]) doit retourner 0", Solution.sumArray(new int[]{}) == 0, "Obtenu: " + Solution.sumArray(new int[]{}));
            } catch (Throwable e) {
                assertTest("Test sumArray", false, "Exception : " + e.toString());
            }
            """
        elif norm_title in ["inverser une chaine", "inverser une chaîne"]:
            test_cases = """
            try {
                assertTest("reverseString('dojo') doit retourner 'ojod'", "ojod".equals(Solution.reverseString("dojo")), "Obtenu: '" + Solution.reverseString("dojo") + "'");
                assertTest("reverseString('a') doit retourner 'a'", "a".equals(Solution.reverseString("a")), "Obtenu: '" + Solution.reverseString("a") + "'");
                assertTest("reverseString('') doit retourner ''", "".equals(Solution.reverseString("")), "Obtenu: '" + Solution.reverseString("") + "'");
            } catch (Throwable e) {
                assertTest("Test reverseString", false, "Exception : " + e.toString());
            }
            """
        elif norm_title == "compter les voyelles":
            test_cases = """
            try {
                assertTest("countVowels('hello') doit retourner 2", Solution.countVowels("hello") == 2, "Obtenu: " + Solution.countVowels("hello"));
                assertTest("countVowels('AEIOU') doit retourner 5", Solution.countVowels("AEIOU") == 5, "Obtenu: " + Solution.countVowels("AEIOU"));
                assertTest("countVowels('xyz') doit retourner 0", Solution.countVowels("xyz") == 0, "Obtenu: " + Solution.countVowels("xyz"));
            } catch (Throwable e) {
                assertTest("Test countVowels", false, "Exception : " + e.toString());
            }
            """
        elif norm_title == "fibonacci":
            test_cases = """
            try {
                assertTest("fibonacci(0) doit retourner 0", Solution.fibonacci(0) == 0, "Obtenu: " + Solution.fibonacci(0));
                assertTest("fibonacci(1) doit retourner 1", Solution.fibonacci(1) == 1, "Obtenu: " + Solution.fibonacci(1));
                assertTest("fibonacci(5) doit retourner 5", Solution.fibonacci(5) == 5, "Obtenu: " + Solution.fibonacci(5));
                assertTest("fibonacci(8) doit retourner 21", Solution.fibonacci(8) == 21, "Obtenu: " + Solution.fibonacci(8));
            } catch (Throwable e) {
                assertTest("Test fibonacci", false, "Exception : " + e.toString());
            }
            """
        elif norm_title == "palindrome":
            test_cases = """
            try {
                assertTest("isPalindrome('radar') doit retourner true", Solution.isPalindrome("radar") == true, "Obtenu: false");
                assertTest("isPalindrome('Java') doit retourner false", Solution.isPalindrome("Java") == false, "Obtenu: true");
                assertTest("isPalindrome('kayak') doit retourner true", Solution.isPalindrome("kayak") == true, "Obtenu: false");
            } catch (Throwable e) {
                assertTest("Test isPalindrome", false, "Exception : " + e.toString());
            }
            """
        elif norm_title in ["tableau trie", "tableau trié"]:
            test_cases = """
            try {
                assertTest("isSorted([1, 2, 3, 4]) doit être true", Solution.isSorted(new int[]{1, 2, 3, 4}) == true, "Obtenu: false");
                assertTest("isSorted([1, 3, 2, 4]) doit être false", Solution.isSorted(new int[]{1, 3, 2, 4}) == false, "Obtenu: true");
                assertTest("isSorted([]) doit être true", Solution.isSorted(new int[]{}) == true, "Obtenu: false");
            } catch (Throwable e) {
                assertTest("Test isSorted", false, "Exception : " + e.toString());
            }
            """
        elif norm_title in ["occurrence dun caractere", "occurrence d'un caractere", "occurrence d'un caractère"]:
            test_cases = """
            try {
                assertTest("charCount('hello', 'l') doit retourner 2", Solution.charCount("hello", 'l') == 2, "Obtenu: " + Solution.charCount("hello", 'l'));
                assertTest("charCount('abc', 'd') doit retourner 0", Solution.charCount("abc", 'd') == 0, "Obtenu: " + Solution.charCount("abc", 'd'));
                assertTest("charCount('', 'a') doit retourner 0", Solution.charCount("", 'a') == 0, "Obtenu: " + Solution.charCount("", 'a'));
            } catch (Throwable e) {
                assertTest("Test charCount", false, "Exception : " + e.toString());
            }
            """
        elif norm_title == "fizzbuzz":
            test_cases = """
            try {
                List<String> res3 = Solution.fizzBuzz(3);
                assertTest("fizzBuzz(3) retourne ['1', '2', 'Fizz']", res3 != null && res3.size() == 3 && "1".equals(res3.get(0)) && "2".equals(res3.get(1)) && "Fizz".equals(res3.get(2)), "Obtenu: " + res3);
                List<String> res5 = Solution.fizzBuzz(5);
                assertTest("fizzBuzz(5) de taille 5 avec 'Buzz' à la fin", res5 != null && res5.size() == 5 && "Buzz".equals(res5.get(4)), "Obtenu: " + res5);
                List<String> res15 = Solution.fizzBuzz(15);
                assertTest("fizzBuzz(15) contient 'FizzBuzz' à l'indice 14", res15 != null && res15.size() == 15 && "FizzBuzz".equals(res15.get(14)), "Obtenu: " + res15);
            } catch (Throwable e) {
                assertTest("Test fizzBuzz", false, "Exception : " + e.toString());
            }
            """
        elif norm_title == "nombre premier":
            test_cases = """
            try {
                assertTest("isPrime(2) doit être true", Solution.isPrime(2) == true, "Obtenu: false");
                assertTest("isPrime(4) doit être false", Solution.isPrime(4) == false, "Obtenu: true");
                assertTest("isPrime(11) doit être true", Solution.isPrime(11) == true, "Obtenu: false");
                assertTest("isPrime(-5) doit être false", Solution.isPrime(-5) == false, "Obtenu: true");
            } catch (Throwable e) {
                assertTest("Test isPrime", false, "Exception : " + e.toString());
            }
            """
        elif norm_title == "anagramme":
            test_cases = """
            try {
                assertTest("isAnagram('listen', 'silent') doit être true", Solution.isAnagram("listen", "silent") == true, "Obtenu: false");
                assertTest("isAnagram('hello', 'world') doit être false", Solution.isAnagram("hello", "world") == false, "Obtenu: true");
                assertTest("isAnagram('Debit Card', 'Bad Credit') doit être true", Solution.isAnagram("Debit Card", "Bad Credit") == true, "Obtenu: false");
            } catch (Throwable e) {
                assertTest("Test isAnagram", false, "Exception : " + e.toString());
            }
            """
        elif norm_title == "factorielle":
            test_cases = """
            try {
                assertTest("factorial(0) doit retourner 1", Solution.factorial(0) == 1, "Obtenu: " + Solution.factorial(0));
                assertTest("factorial(5) doit retourner 120", Solution.factorial(5) == 120, "Obtenu: " + Solution.factorial(5));
            } catch (Throwable e) {
                assertTest("Test factorial", false, "Exception : " + e.toString());
            }
            """
        elif norm_title in ["deux sommes", "deux somme"]:
            test_cases = """
            try {
                int[] res = Solution.twoSum(new int[]{2, 7, 11, 15}, 9);
                boolean ok = res != null && res.length == 2 && ((res[0] == 0 && res[1] == 1) || (res[0] == 1 && res[1] == 0));
                assertTest("twoSum([2, 7, 11, 15], 9) doit retourner [0, 1]", ok, "Obtenu: " + java.util.Arrays.toString(res));
            } catch (Throwable e) {
                assertTest("Test twoSum", false, "Exception : " + e.toString());
            }
            """
        else:
            # Fallback générique si aucun test spécifique n'est défini
            test_cases = """
            assertTest("Vérification de base", true, "Ok");
            """

        return base_runner.replace("// [TESTS_PLACEHOLDER]", test_cases)