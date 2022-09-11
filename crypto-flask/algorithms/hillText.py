#Cryptoanalysis de una sola palabra larga?

import math
import sympy
from algorithms.goodies import InputKeyError
"""
Encrypt y Decrypt reciben (size: int, text: str, key: str)
 donde size es la dimensión de las matrices
 y los textos text y key(solo letras mayúsculas)
 En encrypt se puede no escribir key
Devuelven lista [encriptedText, key], ambos valores son strings de letras mayúsculas

Cryptoanalysis recibe size: int, encryptedTexts: list, plainTexts: list
donde size es la dimensión de las matrices
y encryptedTexts y plainTexts son listas de textos encriptados y claros, respectivamente
Cada una debe constar de size palabras, de las cuales solo se toma en cuenta las primera size letras
Devuelve clave
"""

def hillEncrypt(size: int, text: str, key = None):
    if key == None:
        keyMatrix = randomKeyMatrix(size)
    else:
        checkInput(text, key, size)
        keyMatrix = getMatrix(key, size)
        isInvertibleMod(keyMatrix, 26, "key")

    textMatrix = getTextMatrix(text, size)
    encryptedMatrix = textMatrix * keyMatrix % 26

    encriptedText = getText(encryptedMatrix)
    keyText = getText(keyMatrix)
    return ["".join(encriptedText), keyText]

def hillDecrypt(size: int, text: str, key: str):

    keyMatrix = getMatrix(key, size)
    textVector = getTextMatrix(text, size)

    isInvertibleMod(keyMatrix, 26, "key")
    inverseKeyMatrix = keyMatrix.inv_mod(26)
    decipherMatrix = textVector*inverseKeyMatrix % 26

    inverseKey = getText(inverseKeyMatrix)
    decryptedText = getText(decipherMatrix)

    return [decryptedText, inverseKey]

def hillCryptoAnalysis(size: int, encryptedTexts: list, plainTexts: list):
    checkAnalysisInput(encryptedTexts, plainTexts, size)

    encrypted_list = []
    plain_list = []

    for i in range(size):
        encrypted_list.append(getMatrix(encryptedTexts[i][0:size], size))
        plain_list.append(getMatrix(plainTexts[i][0:size], size))

    encrypted_matrix = sympy.Matrix(encrypted_list)
    plain_matrix = sympy.Matrix(plain_list)
    key_matrix = solveKey(encrypted_matrix, plain_matrix)
    y = plain_matrix*key_matrix%26
    return getText(key_matrix)

def randomKeyMatrix(size: int):
    matrix = sympy.randMatrix(size, min=0, max=26, symmetric=True)
    while math.gcd(matrix.det(), 26) != 1:
        matrix = sympy.randMatrix(size, min=0, max=25, symmetric=True)
    return matrix

#---------------> Matrices

def solveKey(encrypted_matrix: sympy.Matrix, plain_matrix: sympy.Matrix):
    isInvertibleMod(plain_matrix, 26, "plaintexts")
    inv_plain = plain_matrix.inv_mod(26)
    y = plain_matrix * inv_plain %26
    key = inv_plain * encrypted_matrix % 26
    return key

def isInvertibleMod(matrix: sympy.Matrix, n: int , s=""):
    if matrix.rows != matrix.cols:
        raise InputKeyError(s + " matrix must be square")
    det_k = matrix.det()
    if math.gcd(det_k, n) > 1:
        raise InputKeyError(
            "The determinant of the " + s + " matrix must be comprime with 26"
        )

#---------------> Checkers

def checkAnalysisInput(encryptedTexts: list, plainTexts: list, n: int):
    if n not in range(2, 5):
        raise InputKeyError("Matrices must be between 2x2 and 4x4")
    if 1 != len(encryptedTexts) and len(encryptedTexts) != n:
        raise InputKeyError("Insertar "+str(n)+" textos cifrados")
    if 1 != len(plainTexts) and len(plainTexts) != n:
        raise InputKeyError("Insertar "+str(n)+" textos claros")

def checkInput(text:str, key: str, size:int):
    if size < 0 or size > 4:
        raise InputKeyError("Matrix solved up to 4x4")
    if size*2 > len(key):
        raise InputKeyError("Key must be " + str(size*2) + " characters long")
    onlyUppercase_letters(key)
    onlyUppercase_letters(text)

def onlyUppercase_letters(s):
    for i in s:
        if (ord(i) < 65 or 91 < ord(i)):
            raise InputKeyError("text must contain only uppercase letters")
    return True

#---------------> Converters

def getMatrix(text: list, size: int, square=False):
    text_l = list(text)
    matrix_num = []
    for i in range(0, len(text_l), size):
        charList = text_l[i:i+size]
        intList = [ord(j) % 65 for j in charList]
        matrix_num.append(intList)

        if square and len(intList) != len(text_l):
            raise InputKeyError("There must be an equal amount of elements in every column and row")

    return sympy.Matrix(matrix_num)

def getTextMatrix(text: str, size: int):
    #divide list into strings of size length
    text_l = [text[i:i+size] for i in range(0, len(text), size)]
    if len(text_l[-1]) < size:
        text_l[-1] = text_l[-1] + 'A'*(size-len(text_l[-1]))

    for i in range(len(text_l)):
        text_l[i] = [ord(i) % 65 for i in text_l[i]]

    return sympy.Matrix(text_l)

def getText(keyMatrix: sympy.Matrix):
    return "".join([chr(j+65) for j in keyMatrix])



t = "WORLDISFUNINNOS"
k = "NINELETTE"
a = hillEncrypt(3, t, k)
ax = hillDecrypt(3, a[0], a[1])

b = hillEncrypt(3, t)
bx = hillDecrypt(3, a[0], a[1])

"Example invertible matrix mod 26 fxampjtqo"
p_t = ["FXA", "MPJ", "TQOV"]
e_t = ["BHB", "XQS", "FWD"]

y = [hillEncrypt(3, i, k) for i in p_t]
x = hillCryptoAnalysis(3, e_t, p_t) # Debe ser k= NINELETTE
print(x)
