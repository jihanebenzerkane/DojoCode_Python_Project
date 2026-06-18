-- ============================================================
-- CodeDojo -- seed_challenges.sql
-- 15 challenges Java niveau Junior
-- Executer apres init_db.sql
-- ============================================================

USE codedojo;

INSERT INTO challenges (title, description, difficulty, points, language, expected_concepts) VALUES

-- ── NIVEAU DEBUTANT (5 challenges, 10 pts) ───────────────────────────────

('Hello Dojo',
'Ecris une methode sayHello() qui retourne la chaine "Hello, Dojo!". La methode doit etre publique et statique.',
'junior', 10, 'java',
'methode statique, return, String'),

('Pair ou Impair',
'Ecris une methode isEven(int n) qui retourne true si n est pair, false sinon. N''utilise pas de librairie externe.',
'junior', 10, 'java',
'modulo operator, boolean return, conditions'),

('Maximum de deux nombres',
'Ecris une methode max(int a, int b) qui retourne le plus grand des deux entiers sans utiliser Math.max().',
'junior', 10, 'java',
'if-else, comparaison, return'),

('Somme d''un tableau',
'Ecris une methode sumArray(int[] arr) qui retourne la somme de tous les elements d''un tableau d''entiers.',
'junior', 10, 'java',
'boucle for, tableau, accumulation'),

('Inverser une chaine',
'Ecris une methode reverseString(String s) qui retourne la chaine inversee. Exemple: "dojo" -> "ojod".',
'junior', 10, 'java',
'String, boucle, charAt, StringBuilder'),

-- ── NIVEAU INTERMEDIAIRE (5 challenges, 20 pts) ──────────────────────────

('Compter les voyelles',
'Ecris une methode countVowels(String s) qui compte le nombre de voyelles (a,e,i,o,u) dans une chaine, sans tenir compte de la casse.',
'junior', 20, 'java',
'String, boucle, toLowerCase, conditions multiples'),

('Fibonacci',
'Ecris une methode fibonacci(int n) qui retourne le n-ieme terme de la suite de Fibonacci. fibonacci(0)=0, fibonacci(1)=1.',
'junior', 20, 'java',
'recursion ou iteration, cas de base, suite'),

('Palindrome',
'Ecris une methode isPalindrome(String s) qui retourne true si la chaine est un palindrome (se lit pareil dans les deux sens). Ignore la casse.',
'junior', 20, 'java',
'String, reverse, equals, toLowerCase'),

('Tableau trie',
'Ecris une methode isSorted(int[] arr) qui retourne true si le tableau est trie dans l''ordre croissant.',
'junior', 20, 'java',
'boucle, comparaison consecutifs, edge cases tableau vide'),

('Occurrence d''un caractere',
'Ecris une methode charCount(String s, char c) qui retourne le nombre de fois que le caractere c apparait dans la chaine s.',
'junior', 20, 'java',
'String, boucle, charAt, compteur'),

-- ── NIVEAU AVANCE JUNIOR (5 challenges, 30 pts) ──────────────────────────

('FizzBuzz',
'Ecris une methode fizzBuzz(int n) qui retourne une liste de chaines de 1 a n. Pour les multiples de 3: "Fizz", de 5: "Buzz", de 15: "FizzBuzz", sinon le nombre en chaine.',
'junior', 30, 'java',
'ArrayList, modulo, conditions, String.valueOf'),

('Nombre premier',
'Ecris une methode isPrime(int n) qui retourne true si n est un nombre premier. Gere les cas n<=1.',
'junior', 30, 'java',
'boucle, modulo, optimisation sqrt, edge cases'),

('Anagramme',
'Ecris une methode isAnagram(String s1, String s2) qui retourne true si les deux chaines sont des anagrammes (memes lettres, ordre different). Ignore la casse et les espaces.',
'junior', 30, 'java',
'Arrays.sort, toCharArray, toLowerCase, trim'),

('Factorielle',
'Ecris une methode factorial(int n) qui retourne n! (factorielle de n). Gere le cas n=0 (retourne 1). Utilise la recursion.',
'junior', 30, 'java',
'recursion, cas de base, multiplication'),

('Deux sommes',
'Etant donne un tableau d''entiers et une cible, ecris une methode twoSum(int[] nums, int target) qui retourne les indices des deux nombres dont la somme egale target. Suppose qu''il y a exactement une solution.',
'junior', 30, 'java',
'HashMap, indices, iteration, complexite O(n)');

SELECT CONCAT('Challenges inseres: ', COUNT(*), ' / 15 attendus') AS status FROM challenges;